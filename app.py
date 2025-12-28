from flask import Flask, render_template, request, redirect, url_for, session, flash
import sys
import os
import datetime

# Add Services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Services'))

try:
    from Services.OrderHandler import OrdersHandler
    from Services.Customer import Customer
    from Services.Staff import Staff, Driver, RepoStaff, Management, CSStaff
    from Services.CustomerTypes import Normal, Contracted, Sponsored
    from Services.Location import Destination
    from Services.PaymentArrangement import BillingTiming
except ImportError as e:
    print(f"Error importing services: {e}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Initialize OrderHandler
orders_handler = OrdersHandler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_staff = request.form.get('is_staff')

        if is_staff:
            try:
                staff = Staff.from_ID(username)
                if staff.verify(password):
                    session['user_id'] = staff.ID
                    session['is_staff'] = True
                    flash('Login successful!', 'success')
                    return redirect(url_for('staff_dashboard'))
                else:
                    flash('Invalid password', 'error')
            except FileNotFoundError:
                flash('Staff ID not found', 'error')
        else:
            try:
                customer = Customer.from_email(username)
                if customer.verify(password):
                    session['user_id'] = customer.ID
                    session['is_staff'] = False
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password', 'error')
            except ValueError:
                flash('Email not registered', 'error')
            except FileNotFoundError:
                flash('Customer data error', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address_str = request.form.get('address')
        password = request.form.get('password')
        billing_pref_str = request.form.get('billing_pref')

        try:
            billing_pref = getattr(BillingTiming, billing_pref_str)
            address = Destination(address_str)
            
            # Default to Normal customer for web registration
            # In a real app, might want to allow choosing type
            new_customer = Normal(
                first_name=first_name,
                last_name=last_name,
                address=address,
                phone_number=phone,
                email=email,
                password=password,
                billing_pref=billing_pref
            )
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'error')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id') or session.get('is_staff'):
        return redirect(url_for('login'))
    
    try:
        customer = Customer.from_ID(session['user_id'])
        orders = customer.my_orders()
        return render_template('dashboard.html', customer=customer, orders=orders)
    except Exception as e:
        flash(f"Error loading dashboard: {e}", "error")
        return redirect(url_for('logout'))

@app.route('/staff_dashboard')
def staff_dashboard():
    if not session.get('user_id') or not session.get('is_staff'):
        return redirect(url_for('login'))

    try:
        staff = Staff.from_ID(session['user_id'])
        return render_template('staff_dashboard.html', staff=staff)
    except Exception as e:
        flash(f"Error loading staff dashboard: {e}", "error")
        return redirect(url_for('logout'))

@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        return redirect(url_for('order_status', order_id=order_id))
    return render_template('track.html')

@app.route('/order/<order_id>')
def order_status(order_id):
    try:
        order = orders_handler.get(order_id)
        return render_template('order_details.html', order=order)
    except FileNotFoundError:
        flash(f"Order {order_id} not found.", "error")
        return redirect(url_for('track'))
    except Exception as e:
         # Some methods in OrderHandler might raise other exceptions or just fail
        try:
             # fallback if get fails directly (though get should handle it)
            order = orders_handler.get(order_id)
            if order:
                return render_template('order_details.html', order=order)
        except:
            pass
        flash(f"Order {order_id} not found or error occurred.", "error")
        return redirect(url_for('track'))

@app.route('/new_order')
def new_order():
    if not session.get('user_id') or session.get('is_staff'):
        return redirect(url_for('login'))
    # TODO: Implement full order creation form and logic
    flash("New Order feature not fully implemented in web UI yet.", "info")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
