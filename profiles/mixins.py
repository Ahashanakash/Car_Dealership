from django.contrib.auth.mixins import UserPassesTestMixin 
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

error_403_html = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Denied</title>
    <style>
        body {
            background-color: #f8d7da;
            color: #721c24;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            border: 1px solid #f5c6cb;
            background-color: #f8d7da;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            font-size: 48px;
            margin-bottom: 20px;
        }
        p {
            font-size: 18px;
            margin-bottom: 30px;
        }
        a {
            text-decoration: none;
            color: white;
            background-color: #721c24;
            padding: 10px 20px;
            border-radius: 5px;
        }
        a:hover {
            background-color: #501217;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Access Denied</h1>
        <p>You do not have permission to view this page.</p>
        <a href="{% url 'customer_dashboard' %}">Go Back to Dashboard</a>
    </div>
</body>
</html>
"""

class IsCustomerMixin (UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self. request.user, 'is_customer') and self.request.user.is_customer
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden (error_403_html)
        return redirect('login')
    
    
class IsSellerMixin (UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self. request.user, 'is_seller') and self.request.user.is_seller
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden (error_403_html)
        return redirect('login')