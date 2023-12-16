# import frappe
# import requests
# import json
# from frappe import enqueue
# import re

# def user_id(doc):
#     user_email = doc.for_user
#     user_device_id = frappe.get_all("User Device", filters= {"user": user_email}, fields=["device_id"])
#     return user_device_id

# @frappe.whitelist()
# def send_notification(doc):
#     device_ids = user_id(doc)

#     for device_id in device_ids:
#         enqueue(process_notification, queue="default", now=False,\
#                          device_id=device_id, notification=doc)

# def convert_message(message):
#     CLEANR = re.compile('<.*?>')
#     cleanmessage = re.sub(CLEANR, "",message)
#     # cleantitle = re.sub(CLEANR, "",title)
#     return cleanmessage

# def process_notification(device_id, notification):         
#     message = notification.email_content
#     title = notification.subject
#     if message:
#         message = convert_message(message)
#     if title:
#         title = convert_message(title)

#     url = "https://fcm.googleapis.com/fcm/send"
#     body = {
#         "to": device_id.device_id,
#         "notification": {
#             "body": message,
#             "title": title
#         },
#         "data": {
#             "doctype": notification.document_type,
#             "docname": notification.document_name
#         }
#     }

#     server_key = frappe.db.get_single_value('FCM Notification Settings', 'server_key')
#     req = requests.post(url=url, data=json.dumps(body), headers={"Authorization": server_key, \
#                                                                 "Content-Type": "application/json", \
#                                                                 "Accept": "application/json"})



import frappe
import requests
import json
from frappe import enqueue
import re

def user_id(doc):
    user_email = doc.for_user
    user_device_ids = frappe.get_all("User Device", filters={"user": user_email}, fields=["device_id"])
    return user_device_ids

@frappe.whitelist()
def send_notification(doc):
    device_ids = user_id(doc)
    responses = []

    for device_id in device_ids:
        response = enqueue(process_notification, queue="default", now=False,\
                         device_id=device_id, notification=doc)
        responses.append(response)

    return responses

def convert_message(message):
    CLEANR = re.compile('<.*?>')
    cleanmessage = re.sub(CLEANR, "",message)
    return cleanmessage


def notify(doc):
    body = doc.body
    title = doc.title

    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "to": doc.idtopic,
        "notification": {
            "body": body,
            "title": title
        },
        "data": json.loads(doc.data) if doc.data else None
    }
    if (doc.notification_type == "Topic"):
        body["to"] = f"/topics/{doc.idtopic}"

    server_key = frappe.db.get_single_value('FCM Notification Settings', 'server_key')
    headers = {
        "Authorization": server_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url=url, data=json.dumps(body), headers=headers)
    print(response.text)

    # Process the FCM response here if needed
    response_data = response.json() if response.status_code == 200 else None

    # You can return the response_data to capture the FCM server's response for each message
    # doc.server_response = str(response_data)
    frappe.db.set_value("Firebase Notification", doc.name, "server_response", str(response_data))
    return response_data




def process_notification(device_id, notification):
    message = notification.email_content
    title = notification.subject
    if message:
        message = convert_message(message)
    if title:
        title = convert_message(title)

    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "to": f"/topics/{device_id.device_id}",  # Assuming device_id is the topic name
        "notification": {
            "body": message,
            "title": title
        },
        "data": {
            "doctype": notification.document_type,
            "docname": notification.document_name
        }
    }

    server_key = frappe.db.get_single_value('FCM Notification Settings', 'server_key')
    headers = {
        "Authorization": server_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url=url, data=json.dumps(body), headers=headers)

    # Process the FCM response here if needed
    response_data = response.json() if response.status_code == 200 else None

    # You can return the response_data to capture the FCM server's response for each message
    return response_data



