import os
import requests

token = "7058473977:AAGA9XIejfYip6Whi_Yumu3s5DfXrOFwQnI"
chatid = "1458372387"

def telegram_send_file():
	try:
		file_path = input("Enter the full file path to send via Telegram: ").strip()
		
		if not os.path.exists(file_path):
			print("File does not exist.")
			return

		url = f"https://api.telegram.org/bot{token}/sendDocument"
		with open(file_path, "rb") as file:
			files = {"document": file}
			data = {"chat_id": chatid}
			response = requests.post(url, data=data, files=files)

		if response.status_code == 200:
			print("File sent successfully.")
		else:
			print("Failed to send file:", response.text)

	except Exception as e:
		print("An error occurred:", e)

telegram_send_file()
