from flask import Flask, render_template, request, redirect, url_for, session, flash
import sys
import os
import datetime

# Add Services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Services'))

try:
    from OrderHandler import OrdersHandler
    from Customer import Customer
    from Staff import Staff, Driver, RepoStaff, Management, CSStaff
    from CustomerTypes import Normal, Contracted, Sponsored
    from Location import Destination
    from PaymentArrangement import BillingTiming
    from Order import Service
    from logger import get_security_logger
except ImportError as e:
    print(f"Error importing services: {e}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Initialize Loggers
logger = get_security_logger()
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
                    logger.info(f"LOGIN_SUCCESS | Staff Login | ID={staff.ID}")
                    return redirect(url_for('staff_dashboard'))
                else:
                    flash('Invalid password', 'error')
                    logger.warning(f"LOGIN_FAILED | Staff Login | ID={username} | Reason=InvalidPassword")
            except FileNotFoundError:
                flash('Staff ID not found', 'error')
                logger.warning(f"LOGIN_FAILED | Staff Login | ID={username} | Reason=NotFound")
        else:
            try:
                customer = Customer.from_email(username)
                if customer.verify(password):
                    session['user_id'] = customer.ID
                    session['is_staff'] = False
                    flash('Login successful!', 'success')
                    logger.info(f"LOGIN_SUCCESS | Customer Login | ID={customer.ID}")
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password', 'error')
                    logger.warning(f"LOGIN_FAILED | Customer Login | Email={username} | Reason=InvalidPassword")
            except ValueError:
                flash('Email not registered', 'error')
                logger.warning(f"LOGIN_FAILED | Customer Login | Email={username} | Reason=NotRegistered")
            except FileNotFoundError:
                flash('Customer data error', 'error')
                logger.error(f"LOGIN_ERROR | Customer Login | Email={username} | Reason=DataCorrupt")

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
        customer_type = request.form.get('customer_type')

        try:
            billing_pref = getattr(BillingTiming, billing_pref_str)
            address = Destination(address_str)
            
            if customer_type == 'Contracted':
                account = request.form.get('account')
                if not account:
                    raise ValueError("Account number is required for Contracted customers.")
                new_customer = Contracted(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    phone_number=phone,
                    email=email,
                    password=password,
                    account=account
                )
            elif customer_type == 'Sponsored':
                sponsor_id = request.form.get('sponsor_id')
                if not sponsor_id:
                    raise ValueError("Sponsor ID is required for Sponsored customers.")
                
                # Check if sponsor exists and is Contracted (validation done in Sponsored.__init__ but good to catch early)
                # Sponsored.__init__ signature: (sponsor_ID, first_name, last_name, address, phone_number, email, password, billing_pref)
                new_customer = Sponsored(
                    sponsor_id,
                    first_name,
                    last_name,
                    address,
                    phone,
                    email,
                    password,
                    billing_pref
                )
            else: # Default to Normal
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
            logger.info(f"REGISTER_SUCCESS | ID={new_customer.ID} | Email={email} | Type={customer_type}")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'error')
            logger.warning(f"REGISTER_FAILED | Email={email} | Error={str(e)}")

    return render_template('register.html')

@app.route('/logout')
def logout():
    user_id = session.get('user_id', 'Unknown')
    session.clear()
    flash('You have been logged out.', 'info')
    logger.info(f"LOGOUT | ID={user_id}")
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

@app.route('/new_order', methods=['GET', 'POST'])
def new_order():
    if not session.get('user_id') or session.get('is_staff'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Extract form data
            service_str = request.form.get('service')
            bill_timing_str = request.form.get('bill_timing')
            origin_str = request.form.get('origin')
            dest_str = request.form.get('destination')
            is_international = request.form.get('is_international') == 'on'
            
            length = int(request.form.get('length'))
            width = int(request.form.get('width'))
            height = int(request.form.get('height'))
            weight = float(request.form.get('weight'))
            value = float(request.form.get('value'))
            description = request.form.get('description')
            is_dangerous = request.form.get('is_dangerous') == 'on'
            is_fragile = request.form.get('is_fragile') == 'on'
            
            # Create objects
            service = getattr(Service, service_str)
            bill_timing = getattr(BillingTiming, bill_timing_str)
            origin = Destination(origin_str)
            destination = Destination(dest_str)
            package_size = (length, width, height)
            
            customer = Customer.from_ID(session['user_id'])
            
            # Place Order
            # Arguments for Order: bill_timing, service, origin, destination, collector_ID, is_international
            # Arguments for Package: size, weight, value, content_description, is_dangerous, is_fragile
            
            # Note: collector_ID is set to "Pending" initially
            order_id = customer.new_order(
                bill_timing,
                service,
                origin,
                destination,
                "Pending",
                is_international,
                # Package args
                package_size,
                weight,
                value,
                description,
                is_dangerous,
                is_fragile
            )
            
            flash(f"Order created successfully! ID: {order_id}", "success")
            logger.info(f"ORDER_CREATED | ID={order_id} | User={session['user_id']} | Service={service_str}")
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash(f"Order creation failed: {e}", "error")
            logger.warning(f"ORDER_FAILED | User={session.get('user_id')} | Error={str(e)}")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            logger.error(f"ORDER_ERROR | User={session.get('user_id')} | Error={str(e)}")

    return render_template('new_order.html')

if __name__ == '__main__':
    app.run(debug=True)
