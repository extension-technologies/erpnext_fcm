# Copyright (c) 2023, Raheeb and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from fcm_notification.send_notification import notify

class FirebaseNotification(Document):
	def on_submit(self):
		fcm_notification_settings = frappe.get_doc("FCM Notification Settings")
		if fcm_notification_settings.enable_notifications == 1:
			notify(self)
