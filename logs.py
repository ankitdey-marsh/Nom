import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
from discord import app_commands
import logging

def log_writer(interaction)->None:
    print(f"[ {interaction.user.name} ] - [ {interaction.guild.name} ] - ( {interaction.channel.name} ) - ", end="")

def error_logs(e)->None:
    logger = logging.getLogger('Nom')
    logger.setLevel(logging.ERROR)
    log_file = 'error.log'
    path1 = 'logs'
    if not os.path.exists(path1):
        os.makedirs(path1)
    full_log_file_path = os.path.join(path1, log_file)
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    file_handler = logging.FileHandler(full_log_file_path)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.error(f"Error: {e}")