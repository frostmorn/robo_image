import time
import io
from PIL import Image
import telebot
import logging
from telebot import types
image_list = []
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

bot = telebot.TeleBot() # Here you should insert telegram token of your app

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Upload image to check what I could do for u.")

def upload_to_imgur(image):
    imagebytes = io.BytesIO()
    image.save(imagebytes, format)
    imagebytes.name = filename
    imagebytes.seek(0,0)
    
    pass

def scale_to(message, image, filename):
    scale_percentage = 0
    try:
        scale_percentage = float(message.text)
    except:
        bot.reply_to(message, "Invalid params provided")
        send_welcome(message)
        return
    
    width = int(image.width * scale_percentage/100)
    height = int(image.height * scale_percentage/100)
    format = image.format
    image = image.resize((width, height))
    imagebytes = io.BytesIO()
    image.save(imagebytes, format)
    imagebytes.name = filename
    imagebytes.seek(0,0)
    caption = "Result image width " + str(image.width) + " px and height " +str(image.height)+" px"


    bot.send_document(message.chat.id, imagebytes, caption=caption)
    
    

def rotate_to(message, image, filename):
    format = image.format
    rotate_to = 0
    try:
        rotate_to = int(message.text)
    except:
        bot.reply_to(message, "Invalid params provided")
        send_welcome(message)
        return
    
    image = image.rotate(int(rotate_to),resample=PIL.Image.BICUBIC, expand=True)
    imagebytes = io.BytesIO()
    image.save(imagebytes, format)
    imagebytes.name = filename
    imagebytes.seek(0,0)
    caption = "Result image width " + str(image.width) + " px and height " +str(image.height)+" px"
    bot.send_document(message.chat.id, imagebytes, caption=caption)

def resize_to(message, image, filename):
    width = 0
    height = 0

    try:
        width = int(message.text.split("*")[0])
        height = int(message.text.split("*")[1])
    except:
        bot.reply_to(message, "Invalid params provided")
        send_welcome(message)
        return

    format = image.format
    image = image.resize((width, height))
    imagebytes = io.BytesIO()
    image.save(imagebytes, format)
    imagebytes.name = filename
    imagebytes.seek(0,0)
    caption = "Result image width " + str(image.width) + " px and height " +str(image.height)+" px"
    bot.send_document(message.chat.id, imagebytes, caption=caption)

def convert_to(message, image, filename):
    try:
        format = message.text 
        imagebytes = io.BytesIO()
        image.save(imagebytes, format)
        imagebytes.name = filename.split(".")[0]+"."+format
        imagebytes.seek(0,0)
        caption = "Result image width " + str(image.width) + " px and height " +str(image.height)+" px"
    except:
        bot.reply_to(message, "Conversion error. Probably u provided invalid format, or such conversion not avaliable.")
        send_welcome(message)
        return

    bot.send_document(message.chat.id, imagebytes, caption=caption)
def what_we_wanna_do(message, image, filename):
    if message.text == "Scale":
        bot.register_next_step_handler(bot.reply_to(message, "Please enter value in % to which u wanna scale to"), scale_to, image, filename)
    if message.text == "Rotate":
        bot.register_next_step_handler(bot.reply_to(message, "Please enter value in degrees u want to rotate to"), rotate_to, image, filename)
    if message.text == "Resize":
        bot.register_next_step_handler(bot.reply_to(message, "Please enter new image size in format width * height"), resize_to, image, filename)
    if message.text == "Convert":
        markup = types.ReplyKeyboardMarkup()
        markup.one_time_keyboard = True
        markup.row('PNG', 'TIFF', 'GIF', 'JPEG')
        markup.row('TGA', 'BMP', 'PDF', 'DIB')
        sent = bot.reply_to(message, "Please select format u want to convert to", reply_markup=markup)
        bot.register_next_step_handler(sent , convert_to, image, filename)
    if message.text == "Upload to Imgur":
	# TODO : Implement that
    	pass

@bot.message_handler(content_types=["document", "photo"])
def doc_recieved(message):
    try:
        file = 0
        filename = "Result"
        if message.content_type == 'photo':
            buffer_file = bot.get_file(message.photo[-1].file_id)
            file = bot.download_file(buffer_file.file_path)
            filename = "image" + str(buffer_file.file_id) + "." + buffer_file.file_path.split(".")[-1]
            pass
        elif message.content_type == 'document':
            file = bot.download_file(bot.get_file(message.document.file_id).file_path)
            filename = message.document.file_name

        if file != 0:
                image = Image.open(io.BytesIO(file))

                image.filename = filename
                image_list.append({"image":image, "chat_id":message.chat.id})
                markup = types.ReplyKeyboardMarkup()
                markup.one_time_keyboard = True
                markup.row('Scale', 'Rotate')
                markup.row('Resize', 'Convert', 'Upload to Imgur')
                answer = "Size("+str(image.width)+" x " + str(image.height) + " px)\r\nImage format - " + image.format + ". What u wanna do with it?"
                sent = bot.reply_to(message, answer , reply_markup=markup)
                bot.register_next_step_handler(sent, what_we_wanna_do, image, filename)
    except:
        bot.reply_to(message, "Processing error happened. Probably this file format not supported yet.")
        send_welcome(message)
        return

while 1:
    try:
        bot.polling()
    except:
        time.sleep(10)
        print("Network Disconnected.")
