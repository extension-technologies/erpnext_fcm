import frappe


def after_insert(self, method=None):
    frappe.call("fcm_notification.send_notification.send_notification", doc=self)
