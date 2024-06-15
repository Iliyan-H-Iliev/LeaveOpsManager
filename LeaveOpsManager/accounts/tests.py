# from django.test import TestCase
#
# # Create your tests here.
# import unittest
# from django import forms
#
# from LeaveOpsManager.accounts.forms import SignupEmployeeForm
#
#
# class TestSignupEmployeeFormInitialization(unittest.TestCase):
#
#     def test_request_none(self):
#         form = SignupEmployeeForm(request=None)
#         with self.assertRaises(forms.ValidationError):
#             form.__init__()
#
#     def test_user_none(self):
#         form = SignupEmployeeForm(request=MockUser(user=None))
#         with self.assertRaises(forms.ValidationError):
#             form.__init__()
#
#     def test_user_not_authenticated(self):
#         form = SignupEmployeeForm(request=MockUser(user=MockUser(authenticated=False)))
#         with self.assertRaises(forms.ValidationError):
#             form.__init__()
#
#     def test_user_type_not_allowed(self):
#         form = SignupEmployeeForm(request=MockUser(user=MockUser(user_type="Admin")))
#         with self.assertRaises(forms.ValidationError):
#             form.__init__()
#
#     def test_company_none(self):
#         form = SignupEmployeeForm(request=MockUser(user=MockUser(company=None)))
#         with self.assertRaises(forms.ValidationError):
#             form.__init__()
#
#
# # Mock classes for testing
# class MockUser:
#     def __init__(self, user=None, authenticated=True, user_type="HR", company=None):
#         self.user = user
#         self.authenticated = authenticated
#         self.user_type = user_type
#         self.company = company
#
#
# if __name__ == '__main__':
#     unittest.main()
