import os
import re
import json
import uuid
import secrets
import string
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

auth_bp = Blueprint('auth', __name__)

# Password complexity regex: >= 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>_~\-+=])[A-Za-z\d!@#$%^&*(),.?":{}|<>_~\-+=]{8,}$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def sanitize_input(text):
    if not isinstance(text, str):
        return text
    return text.strip()

def validate_password_complexity(password):
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one numeric digit (0-9)."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_~\-+=]', password):
        return False, "Password must contain at least one special character (!@#$%^&* etc.)."
    return True, "Password is strong."

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']

def verify_csrf_token(token):
    return session.get('csrf_token') and session.get('csrf_token') == token

@auth_bp.route('/api/auth/status', methods=['GET'])
def get_auth_status():
    csrf_token = generate_csrf_token()
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    
    if not user_id:
        return jsonify({
            'success': True,
            'logged_in': False,
            'is_guest': is_guest,
            'csrf_token': csrf_token,
            'user': None
        })
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, phone, role, email_verified, created_at, last_login FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        u_dict = dict(user)
        return jsonify({
            'success': True,
            'logged_in': True,
            'is_guest': False,
            'csrf_token': csrf_token,
            'user': u_dict
        })
        
    # If session user deleted, clear session
    session.clear()
    return jsonify({
        'success': True,
        'logged_in': False,
        'is_guest': is_guest,
        'csrf_token': csrf_token,
        'user': None
    })

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json or request.form or {}
    
    full_name = sanitize_input(data.get('full_name', ''))
    email = sanitize_input(data.get('email', '')).lower()
    phone = sanitize_input(data.get('phone', ''))
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    role = sanitize_input(data.get('role', 'buyer')).lower()
    
    if not full_name:
        return jsonify({'success': False, 'message': 'Full name is required.'}), 400
        
    if not email or not EMAIL_REGEX.match(email):
        return jsonify({'success': False, 'message': 'Please provide a valid email address.'}), 400
        
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400
        
    is_valid, msg = validate_password_complexity(password)
    if not is_valid:
        return jsonify({'success': False, 'message': msg}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'An account with this email address already exists.'}), 400
        
    user_id = f"user_{uuid.uuid4().hex[:10]}"
    password_hash = generate_password_hash(password)
    
    cursor.execute("""
        INSERT INTO users (id, full_name, email, phone, password_hash, role, email_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, full_name, email, phone, password_hash, role, 1))
    
    conn.commit()
    conn.close()
    
    # Auto-login after signup
    session.clear()
    session['user_id'] = user_id
    session['user_name'] = full_name
    session['user_email'] = email
    session['user_role'] = role
    session['is_guest'] = False
    generate_csrf_token()
    
    return jsonify({
        'success': True,
        'message': 'Account created successfully! Welcome to Karigar Setu.',
        'user': {
            'id': user_id,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'role': role,
            'email_verified': 1
        }
    })

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or request.form or {}
    
    email = sanitize_input(data.get('email', '')).lower()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
        
    u_dict = dict(user)
    
    # Rate Limiting & Lockout Check
    if u_dict.get('lockout_until'):
        lockout_time = datetime.fromisoformat(u_dict['lockout_until']) if isinstance(u_dict['lockout_until'], str) else u_dict['lockout_until']
        if datetime.utcnow() < lockout_time:
            remaining_mins = max(1, int((lockout_time - datetime.utcnow()).total_seconds() / 60))
            conn.close()
            return jsonify({
                'success': False,
                'message': f'Account locked due to multiple failed login attempts. Please try again in {remaining_mins} minute(s).'
            }), 429

    # Verify Password
    if not check_password_hash(u_dict['password_hash'], password):
        failed_attempts = (u_dict.get('failed_login_attempts') or 0) + 1
        lockout_until = None
        
        if failed_attempts >= 5:
            lockout_until = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            msg = "Too many failed attempts. Account locked for 15 minutes."
        else:
            msg = f"Invalid email or password. {5 - failed_attempts} attempt(s) remaining before lockout."
            
        cursor.execute("UPDATE users SET failed_login_attempts = ?, lockout_until = ? WHERE id = ?",
                       (failed_attempts, lockout_until, u_dict['id']))
        conn.commit()
        conn.close()
        return jsonify({'success': False, 'message': msg}), 401

    # Reset lockout counters & update last_login
    now_iso = datetime.utcnow().isoformat()
    cursor.execute("UPDATE users SET failed_login_attempts = 0, lockout_until = NULL, last_login = ? WHERE id = ?",
                   (now_iso, u_dict['id']))
    conn.commit()
    conn.close()

    # Establish Session
    session.clear()
    session['user_id'] = u_dict['id']
    session['user_name'] = u_dict['full_name']
    session['user_email'] = u_dict['email']
    session['user_role'] = u_dict['role']
    session['is_guest'] = False
    
    if remember_me:
        session.permanent = True
        
    generate_csrf_token()
    
    return jsonify({
        'success': True,
        'message': f"Welcome back, {u_dict['full_name']}!",
        'user': {
            'id': u_dict['id'],
            'full_name': u_dict['full_name'],
            'email': u_dict['email'],
            'phone': u_dict['phone'],
            'role': u_dict['role'],
            'email_verified': u_dict['email_verified']
        }
    })

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json or request.form or {}
    email = sanitize_input(data.get('email', '')).lower()
    
    if not email or not EMAIL_REGEX.match(email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address.'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        # Return generic message to prevent email enumeration
        return jsonify({
            'success': True,
            'message': 'If an account exists with this email, a 6-digit OTP reset code has been generated.',
            'otp_demo': None
        })
        
    # Generate 6-digit numeric OTP valid for 10 minutes
    otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))
    expires_at = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    
    cursor.execute("UPDATE users SET otp_code = ?, otp_expires_at = ? WHERE email = ?", (otp_code, expires_at, email))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f"6-digit OTP generated! Code valid for 10 minutes.",
        'otp_demo': otp_code # Included for immediate demo testing
    })

@auth_bp.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json or request.form or {}
    email = sanitize_input(data.get('email', '')).lower()
    otp_code = sanitize_input(data.get('otp_code', ''))
    
    if not email or not otp_code:
        return jsonify({'success': False, 'message': 'Email and OTP code are required.'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, otp_code, otp_expires_at FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not user['otp_code']:
        return jsonify({'success': False, 'message': 'Invalid OTP or no reset requested.'}), 400
        
    if user['otp_code'] != otp_code:
        return jsonify({'success': False, 'message': 'Incorrect 6-digit OTP code. Please try again.'}), 400
        
    expires_at = datetime.fromisoformat(user['otp_expires_at']) if isinstance(user['otp_expires_at'], str) else user['otp_expires_at']
    if datetime.utcnow() > expires_at:
        return jsonify({'success': False, 'message': 'OTP code has expired. Please request a new code.'}), 400
        
    return jsonify({
        'success': True,
        'message': 'OTP code verified successfully! You may now create your new password.'
    })

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.json or request.form or {}
    email = sanitize_input(data.get('email', '')).lower()
    otp_code = sanitize_input(data.get('otp_code', ''))
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not email or not otp_code or not new_password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
        
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400
        
    is_valid, msg = validate_password_complexity(new_password)
    if not is_valid:
        return jsonify({'success': False, 'message': msg}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, otp_code, otp_expires_at FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user or user['otp_code'] != otp_code:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid OTP authorization.'}), 400
        
    new_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET password_hash = ?, otp_code = NULL, otp_expires_at = NULL, failed_login_attempts = 0, lockout_until = NULL WHERE email = ?",
                   (new_hash, email))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Password reset successful! You can now log in with your new password.'
    })

@auth_bp.route('/api/auth/guest', methods=['POST'])
def continue_as_guest():
    session.clear()
    session['is_guest'] = True
    session['user_name'] = 'Guest User'
    generate_csrf_token()
    return jsonify({'success': True, 'is_guest': True, 'message': 'Browsing in Guest Mode.'})

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@auth_bp.route('/api/auth/profile', methods=['PUT'])
def update_profile():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Authentication required.'}), 401
        
    data = request.json or request.form or {}
    full_name = sanitize_input(data.get('full_name', ''))
    phone = sanitize_input(data.get('phone', ''))
    
    if not full_name:
        return jsonify({'success': False, 'message': 'Full name cannot be empty.'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET full_name = ?, phone = ? WHERE id = ?", (full_name, phone, session['user_id']))
    conn.commit()
    conn.close()
    
    session['user_name'] = full_name
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully!',
        'user': {
            'id': session['user_id'],
            'full_name': full_name,
            'phone': phone,
            'email': session.get('user_email')
        }
    })

@auth_bp.route('/api/auth/change-password', methods=['POST'])
def change_password():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Authentication required.'}), 401
        
    data = request.json or request.form or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'Current and new passwords are required.'}), 400
        
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match.'}), 400
        
    is_valid, msg = validate_password_complexity(new_password)
    if not is_valid:
        return jsonify({'success': False, 'message': msg}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user['password_hash'], current_password):
        conn.close()
        return jsonify({'success': False, 'message': 'Current password is incorrect.'}), 400
        
    new_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Password updated successfully!'})
