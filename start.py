import subprocess
import time
import webbrowser

print("🚀 Запуск Timelyx Portfolio System...")

# Запускаем Flask сервер
print("📡 Запуск сервера...")
server = subprocess.Popen(['python', 'flask_server.py'])
time.sleep(2)

# Открываем сайт в браузере
print("🌐 Открываем сайт...")
webbrowser.open('index.html')

print("\n✅ Всё запущено!")
print("📝 Для остановки нажмите Ctrl+C")

try:
    # Держим процесс сервера запущенным
    server.wait()
except KeyboardInterrupt:
    print("\n🛑 Остановка сервера...")
    server.terminate()
