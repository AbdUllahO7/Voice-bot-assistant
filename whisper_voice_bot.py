import asyncio
import platform
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
import os
import pyaudio
import wave
import threading
from typing import Dict, List, Optional, Tuple
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import json
from datetime import datetime
import random
import re
import time
import openai
import requests
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration
try:
    # Force reload config in case it's cached
    import importlib
    if 'config' in globals():
        importlib.reload(config)
    else:
        import config
    CONFIG_LOADED = True
    logger.info("✅ Configuration loaded successfully")
    
    # Immediate validation
    if hasattr(config, 'OPENAI_API_KEY'):
        api_key_preview = config.OPENAI_API_KEY[:15] + "..." if len(config.OPENAI_API_KEY) > 15 else config.OPENAI_API_KEY
        logger.info(f"🔑 API Key loaded: {api_key_preview} (length: {len(config.OPENAI_API_KEY)})")
    else:
        logger.error("❌ OPENAI_API_KEY not found in config")
        
except ImportError as e:
    CONFIG_LOADED = False
    logger.error(f"❌ config.py not found: {e}")
    print("⚠️  config.py not found! Please copy config_template.py to config.py and fill in your API keys.")
except Exception as e:
    CONFIG_LOADED = False
    logger.error(f"❌ Error loading config.py: {e}")
    print(f"⚠️  Error loading config.py: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceRestaurantGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Initialize voice system
        self.service_account_path = '/Users/abdullahalhasan/Desktop/Abdullah Alhasan/whisper_voice_bot/service-account-key.json'
        try:
            self.speech_client = speech.SpeechClient.from_service_account_json(self.service_account_path)
            self.tts_client = texttospeech.TextToSpeechClient.from_service_account_json(self.service_account_path)
            self.voice_enabled = True
        except Exception as e:
            self.voice_enabled = False
            logger.warning(f"Voice system initialization failed: {e}")
        
        # Initialize GPT for better conversation understanding
        # You need to set your OpenAI API key here
        self.openai_api_key = "your-openai-api-key-here"  # Replace with your actual API key
        self.gpt_enabled = bool(self.openai_api_key and self.openai_api_key != "your-openai-api-key-here")
        self.available_models = []
        
        if self.gpt_enabled:
            try:
                openai.api_key = self.openai_api_key
                # Test the connection and get available models
                models_response = openai.models.list()
                all_models = [model.id for model in models_response.data]
                
                # Check which GPT models are available
                preferred_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
                self.available_models = [model for model in preferred_models if model in all_models]
                
                if self.available_models:
                    logger.info(f"GPT integration enabled with models: {', '.join(self.available_models)}")
                else:
                    self.gpt_enabled = False
                    logger.warning("No compatible GPT models found")
                    
            except Exception as e:
                self.gpt_enabled = False
                logger.warning(f"GPT initialization failed: {e}")
        else:
            logger.warning("GPT integration disabled - please set your OpenAI API key")
        
        # Enhanced menu data with descriptions
        self.menu = {
            "🍔 Signature Burgers": {
                "Joe's Classic Burger": {
                    "price": 12.99,
                    "description": "Juicy beef patty, lettuce, tomato, onion, special sauce"
                },
                "Ultimate Cheeseburger": {
                    "price": 14.99,
                    "description": "Double cheese, beef patty, crispy bacon, lettuce"
                },
                "BBQ Bacon Deluxe": {
                    "price": 16.99,
                    "description": "BBQ sauce, crispy bacon, onion rings, cheddar"
                },
                "Garden Veggie Burger": {
                    "price": 13.99,
                    "description": "House-made veggie patty, avocado, sprouts"
                },
                "Grilled Chicken Supreme": {
                    "price": 15.99,
                    "description": "Marinated chicken breast, swiss cheese, honey mustard"
                }
            },
            "🍟 Sides & Starters": {
                "Crispy French Fries": {
                    "price": 4.99,
                    "description": "Golden crispy fries with sea salt"
                },
                "Beer Battered Onion Rings": {
                    "price": 5.99,
                    "description": "Thick cut onions in crispy beer batter"
                },
                "Mozzarella Sticks": {
                    "price": 6.99,
                    "description": "Six pieces with marinara dipping sauce"
                },
                "Fresh Coleslaw": {
                    "price": 3.99,
                    "description": "Crisp cabbage with creamy house dressing"
                },
                "Garden Side Salad": {
                    "price": 4.99,
                    "description": "Mixed greens, tomatoes, cucumbers, choice of dressing"
                }
            },
            "🥤 Beverages": {
                "Coca-Cola": {
                    "price": 2.99,
                    "description": "Classic cola, ice cold"
                },
                "Sprite": {
                    "price": 2.99,
                    "description": "Crisp lemon-lime soda"
                },
                "Fresh Orange Juice": {
                    "price": 3.99,
                    "description": "Freshly squeezed orange juice"
                },
                "Bottled Water": {
                    "price": 1.99,
                    "description": "Premium spring water"
                },
                "Creamy Milkshake": {
                    "price": 5.99,
                    "description": "Vanilla, chocolate, or strawberry"
                },
                "Premium Coffee": {
                    "price": 2.49,
                    "description": "Fresh roasted, hot brewed coffee"
                }
            },
            "🍰 Sweet Endings": {
                "Triple Chocolate Cake": {
                    "price": 6.99,
                    "description": "Rich chocolate cake with chocolate frosting"
                },
                "Vanilla Ice Cream": {
                    "price": 4.99,
                    "description": "Premium vanilla ice cream, two scoops"
                },
                "Homemade Apple Pie": {
                    "price": 5.99,
                    "description": "Warm apple pie with cinnamon"
                },
                "Chocolate Chip Cookies": {
                    "price": 3.99,
                    "description": "Fresh baked, warm and gooey"
                }
            }
        }
        
        # Enhanced conversation system
        self.conversation_context = {
            "stage": "greeting",  # greeting, ordering, confirming, checkout
            "last_item": None,
            "suggested_items": [],
            "customer_preferences": [],
            "order_count": 0
        }
        
        # Order tracking
        self.current_order = []
        self.total_price = 0.0
        self.is_listening = False
        self.customer_name = "friend"
        
        # Enhanced keywords and responses
        self.affirmative_words = ["yes", "yeah", "yep", "sure", "okay", "ok", "correct", "right", "sounds good", "perfect", "exactly"]
        self.negative_words = ["no", "nope", "nah", "wrong", "incorrect", "not really", "change that"]
        self.done_words = ["done", "finished", "complete", "that's all", "nothing else", "no more", "finish order", "check out"]
        self.help_words = ["help", "recommend", "suggest", "what's good", "popular", "best"]
        
        # Number word mappings for quantity detection
        self.number_words = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "a": 1, "an": 1, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
            "6": 6, "7": 7, "8": 8, "9": 9, "10": 10
        }
        
        self.greeting_responses = [
            "Hello and welcome to Joe's Restaurant! I'm your smart AI assistant powered by advanced language understanding. I can help you place orders naturally - just say 'I want two burgers and fries' or 'Can I get one chocolate cake?' I also understand modifications like 'remove the coca-cola' or 'cancel my burger.' You can ask me 'what do you recommend?' for suggestions. What would you like to start with today?",
            "Hi there! Thanks for choosing Joe's. I'm your intelligent voice assistant that understands natural conversation. You can speak normally - say things like 'I'll have three milkshakes' or 'Give me one classic burger and two fries.' If you change your mind, just say 'remove the fries' or 'cancel that burger.' I can also provide recommendations when you ask. What sounds good to you?",
            "Welcome to Joe's Restaurant! I'm your AI-powered ordering assistant with advanced conversation abilities. I understand quantities, modifications, and natural language. Feel free to say 'two ice creams' or 'remove the soda' or 'change my fries to onion rings.' I can give you recommendations if you ask 'what's popular?' When you're finished, just say 'that's all' or 'checkout.' What can I get started for you?",
            "Good day! I'm Joe's advanced voice assistant with smart language understanding. You can speak naturally - try saying 'I want two burgers' or 'remove the coca-cola from my order.' I understand modifications, quantities, and can suggest popular items. When you're done, just say 'finished' or 'that's it.' What delicious items would you like today?"
        ]
        
        # Add model-specific greeting if GPT is enabled
        if self.gpt_enabled and self.available_models:
            best_model = self.available_models[0]
            model_greeting = f"Hello! I'm powered by {best_model.upper()} for the most natural conversation experience. I can understand complex requests like 'remove the burger and add two fries instead' or 'cancel my order and start over.' Just speak naturally - what would you like to order today?"
            self.greeting_responses.insert(0, model_greeting)
        
        self.encouragement_phrases = [
            "Great choice!",
            "Excellent selection!",
            "That's one of our favorites!",
            "Perfect!",
            "Wonderful choice!",
            "You've got great taste!",
            "Smart pick!",
            "Outstanding choice!"
        ]
        
        self.transition_phrases = [
            "What else can I add to your order?",
            "Anything else looking good to you?",
            "What else would you like to try? You can say quantities like 'two sodas' or 'three cookies.'",
            "Can I get you anything else? Remember, you can specify how many you want, or say 'remove' if you change your mind.",
            "What else sounds delicious?",
            "Shall we add anything else? Feel free to tell me how many of each item you'd like, or say 'cancel' if you want to remove something.",
            "Would you like to add more items? Just say the quantity and item name, or 'remove the [item]' to take something off.",
            "What other tasty items can I add for you? You can also modify your order by saying 'remove' or 'cancel' any item."
        ]
        
        self.setup_professional_gui()
        self.update_order_display()
        
        # Auto-start with greeting
        if self.voice_enabled:
            self.root.after(2000, self.start_voice_ordering)

    def setup_window(self):
        """Setup main window with modern styling."""
        self.root.title("Joe's Restaurant - Professional Voice Ordering")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8fafc')
        self.root.resizable(True, True)
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom styles
        self.style.configure('Header.TLabel', 
                           font=('Segoe UI', 24, 'bold'),
                           background='#1e293b',
                           foreground='white')
        
        self.style.configure('Subheader.TLabel',
                           font=('Segoe UI', 12),
                           background='#1e293b',
                           foreground='#cbd5e1')
        
        self.style.configure('Modern.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(20, 10))

    def setup_professional_gui(self):
        """Create a modern, professional GUI layout."""
        # Main container with padding
        main_container = tk.Frame(self.root, bg='#f8fafc')
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Professional Header
        self.create_header(main_container)
        
        # Main content area with modern layout
        content_container = tk.Frame(main_container, bg='#f8fafc')
        content_container.pack(fill='both', expand=True, pady=20)
        
        # Create three main panels
        self.create_menu_panel(content_container)
        self.create_order_panel(content_container)
        self.create_voice_panel(content_container)

    def create_header(self, parent):
        """Create professional header section."""
        header_frame = tk.Frame(parent, bg='#1e293b', height=120)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Restaurant branding
        brand_frame = tk.Frame(header_frame, bg='#1e293b')
        brand_frame.pack(expand=True, fill='both')
        
        title_label = tk.Label(brand_frame, text="🍔 Joe's Restaurant", 
                              font=('Segoe UI', 28, 'bold'), 
                              fg='white', bg='#1e293b')
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(brand_frame, 
                                 text="Premium Voice & Touch Ordering Experience", 
                                 font=('Segoe UI', 14), 
                                 fg='#94a3b8', bg='#1e293b')
        subtitle_label.pack()
        
        # Status indicator with specific GPT model info
        status_text = "● Ready"
        status_color = '#22c55e'
        
        if self.gpt_enabled and self.available_models:
            best_model = self.available_models[0].upper()
            status_text += f" ({best_model} Enhanced)"
        elif self.gpt_enabled:
            status_text += " (AI Basic)"
            status_color = '#f59e0b'
        elif not self.voice_enabled:
            status_text = "● Voice Disabled"
            status_color = '#f59e0b'
        
        self.header_status = tk.Label(brand_frame, text=status_text, 
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=status_color, bg='#1e293b')
        self.header_status.pack(pady=(5, 0))

    def create_menu_panel(self, parent):
        """Create modern menu display panel."""
        menu_frame = tk.Frame(parent, bg='white', relief='flat', bd=0)
        menu_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Menu header with modern styling
        menu_header = tk.Frame(menu_frame, bg='#475569', height=60)
        menu_header.pack(fill='x')
        menu_header.pack_propagate(False)
        
        menu_title = tk.Label(menu_header, text="📋 Our Menu", 
                             font=('Segoe UI', 18, 'bold'),
                             fg='white', bg='#475569')
        menu_title.pack(expand=True)
        
        # Modern tabbed menu
        self.menu_notebook = ttk.Notebook(menu_frame)
        self.menu_notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.setup_modern_menu_tabs()

    def create_order_panel(self, parent):
        """Create modern order display panel."""
        order_frame = tk.Frame(parent, bg='white', relief='flat', bd=0, width=400)
        order_frame.pack(side='right', fill='y', padx=(0, 15))
        order_frame.pack_propagate(False)
        
        # Order header
        order_header = tk.Frame(order_frame, bg='#059669', height=60)
        order_header.pack(fill='x')
        order_header.pack_propagate(False)
        
        order_title = tk.Label(order_header, text="🛒 Your Order", 
                              font=('Segoe UI', 18, 'bold'),
                              fg='white', bg='#059669')
        order_title.pack(expand=True)
        
        # Order content
        order_content = tk.Frame(order_frame, bg='white')
        order_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Enhanced order listbox
        self.setup_order_display(order_content)
        
        # Total display
        total_frame = tk.Frame(order_content, bg='#f1f5f9', relief='flat', bd=1)
        total_frame.pack(fill='x', pady=10)
        
        self.total_label = tk.Label(total_frame, text="Total: $0.00", 
                                   font=('Segoe UI', 20, 'bold'), 
                                   fg='#dc2626', bg='#f1f5f9')
        self.total_label.pack(pady=15)
        
        # Professional action buttons
        self.create_action_buttons(order_content)

    def create_voice_panel(self, parent):
        """Create modern voice control panel."""
        voice_frame = tk.Frame(parent, bg='white', relief='flat', bd=0, width=350)
        voice_frame.pack(side='right', fill='y')
        voice_frame.pack_propagate(False)
        
        # Voice header
        voice_header = tk.Frame(voice_frame, bg='#7c3aed', height=60)
        voice_header.pack(fill='x')
        voice_header.pack_propagate(False)
        
        voice_title_text = "🎤 AI Voice Assistant"
        if self.gpt_enabled and self.available_models:
            model_name = self.available_models[0].upper()
            voice_title_text += f" ({model_name})"
        elif self.gpt_enabled:
            voice_title_text += " (Basic AI)"
        
        voice_title = tk.Label(voice_header, text=voice_title_text, 
                              font=('Segoe UI', 18, 'bold'),
                              fg='white', bg='#7c3aed')
        voice_title.pack(expand=True)
        
        # Voice content
        voice_content = tk.Frame(voice_frame, bg='white')
        voice_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Voice control button
        self.voice_button = tk.Button(voice_content, 
                                     text="🎤 Start Voice Order", 
                                     font=('Segoe UI', 14, 'bold'), 
                                     bg='#16a34a', 
                                     fg='white',
                                     relief='flat',
                                     command=self.toggle_voice_ordering, 
                                     padx=30, 
                                     pady=15,
                                     cursor='hand2')
        self.voice_button.pack(pady=10)
        
        # Status display with enhanced capabilities info
        status_frame = tk.Frame(voice_content, bg='#f8fafc', relief='flat', bd=1)
        status_frame.pack(fill='x', pady=10)
        
        initial_status = "Ready to take your order with advanced AI understanding!"
        if self.gpt_enabled:
            initial_status += "\n💡 I can understand: 'remove the burger', 'cancel my fries', 'change that to onion rings'"
        
        self.status_label = tk.Label(status_frame, 
                                    text=initial_status, 
                                    font=('Segoe UI', 11), 
                                    fg='#475569', 
                                    bg='#f8fafc',
                                    wraplength=300,
                                    justify='center')
        self.status_label.pack(pady=15)
        
        # Conversation log with modern styling
        log_label = tk.Label(voice_content, text="💬 Conversation", 
                            font=('Segoe UI', 14, 'bold'), 
                            bg='white', fg='#1e293b')
        log_label.pack(anchor='w', pady=(20, 10))
        
        log_frame = tk.Frame(voice_content, bg='#f1f5f9', relief='flat', bd=1)
        log_frame.pack(fill='both', expand=True)
        
        self.conversation_log = ScrolledText(log_frame, 
                                           height=12, 
                                           font=('Segoe UI', 10),
                                           bg='#f8fafc', 
                                           fg='#374151',
                                           wrap='word',
                                           relief='flat',
                                           bd=0)
        self.conversation_log.pack(fill='both', expand=True, padx=10, pady=10)

    def setup_modern_menu_tabs(self):
        """Create modern menu category tabs."""
        for category, items in self.menu.items():
            tab_frame = tk.Frame(self.menu_notebook, bg='white')
            self.menu_notebook.add(tab_frame, text=category)
            
            # Scrollable content
            canvas = tk.Canvas(tab_frame, bg='white', highlightthickness=0)
            scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Create modern menu items
            for i, (item, details) in enumerate(items.items()):
                self.create_menu_item(scrollable_frame, item, details, category)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

    def create_menu_item(self, parent, item_name, details, category):
        """Create a modern menu item card."""
        item_card = tk.Frame(parent, bg='#f8fafc', relief='flat', bd=1)
        item_card.pack(fill='x', padx=10, pady=8)
        
        # Item content frame
        content_frame = tk.Frame(item_card, bg='#f8fafc')
        content_frame.pack(fill='x', padx=15, pady=15)
        
        # Item name and price header
        header_frame = tk.Frame(content_frame, bg='#f8fafc')
        header_frame.pack(fill='x')
        
        item_label = tk.Label(header_frame, text=item_name, 
                             font=('Segoe UI', 14, 'bold'),
                             bg='#f8fafc', fg='#1e293b', anchor='w')
        item_label.pack(side='left')
        
        price_label = tk.Label(header_frame, text=f"${details['price']:.2f}", 
                              font=('Segoe UI', 16, 'bold'), 
                              fg='#059669', bg='#f8fafc')
        price_label.pack(side='right')
        
        # Description
        desc_label = tk.Label(content_frame, text=details['description'], 
                             font=('Segoe UI', 10), 
                             fg='#64748b', bg='#f8fafc',
                             wraplength=400, justify='left', anchor='w')
        desc_label.pack(fill='x', pady=(5, 10))
        
        # Add button
        add_button = tk.Button(content_frame, text="Add to Order", 
                              command=lambda: self.add_to_order_gui(item_name, details['price'], category),
                              bg='#3b82f6', fg='white', 
                              font=('Segoe UI', 11, 'bold'),
                              relief='flat', padx=20, pady=8,
                              cursor='hand2')
        add_button.pack(anchor='e')

    def setup_order_display(self, parent):
        """Setup enhanced order display."""
        order_list_frame = tk.Frame(parent, bg='#f8fafc', relief='flat', bd=1)
        order_list_frame.pack(fill='both', expand=True, pady=10)
        
        self.order_listbox = tk.Listbox(order_list_frame, 
                                       font=('Segoe UI', 11), 
                                       bg='#f8fafc',
                                       fg='#374151',
                                       selectbackground='#e0e7ff',
                                       relief='flat',
                                       bd=0)
        order_scrollbar = ttk.Scrollbar(order_list_frame, orient='vertical')
        order_scrollbar.pack(side='right', fill='y', padx=(0, 10))
        self.order_listbox.pack(side='left', fill='both', expand=True, padx=15, pady=15)
        self.order_listbox.config(yscrollcommand=order_scrollbar.set)
        order_scrollbar.config(command=self.order_listbox.yview)

    def create_action_buttons(self, parent):
        """Create professional action buttons."""
        button_frame = tk.Frame(parent, bg='white')
        button_frame.pack(fill='x', pady=15)
        
        # Left side buttons
        left_buttons = tk.Frame(button_frame, bg='white')
        left_buttons.pack(side='left')
        
        clear_button = tk.Button(left_buttons, text="Clear Order", 
                                command=self.clear_order, 
                                bg='#ef4444', fg='white',
                                font=('Segoe UI', 10, 'bold'), 
                                relief='flat',
                                padx=20, pady=8,
                                cursor='hand2')
        clear_button.pack(side='left', padx=(0, 5))
        
        remove_button = tk.Button(left_buttons, text="Remove Selected", 
                                 command=self.remove_selected_item, 
                                 bg='#f59e0b', fg='white',
                                 font=('Segoe UI', 10, 'bold'), 
                                 relief='flat',
                                 padx=20, pady=8,
                                 cursor='hand2')
        remove_button.pack(side='left')
        
        # Right side button
        checkout_button = tk.Button(button_frame, text="Checkout", 
                                   command=self.checkout, 
                                   bg='#059669', fg='white',
                                   font=('Segoe UI', 11, 'bold'), 
                                   relief='flat',
                                   padx=25, pady=10,
                                   cursor='hand2')
        checkout_button.pack(side='right')

    def remove_selected_item(self):
        """Remove the selected item from the order."""
        try:
            selection = self.order_listbox.curselection()
            if not selection:
                messagebox.showinfo("No Selection", "Please select an item to remove from your order.")
                return
            
            selected_index = selection[0]
            
            if not self.current_order:
                return
            
            # Get grouped items for display mapping
            item_counts = {}
            item_positions = {}  # Track original positions
            
            for i, order_item in enumerate(self.current_order):
                item_name = order_item['item']
                if item_name not in item_counts:
                    item_counts[item_name] = {'count': 0, 'positions': []}
                item_counts[item_name]['count'] += 1
                item_counts[item_name]['positions'].append(i)
            
            # Find which item group was selected
            item_names = list(item_counts.keys())
            if selected_index < len(item_names):
                selected_item_name = item_names[selected_index]
                
                # Remove one instance of this item (last occurrence)
                positions = item_counts[selected_item_name]['positions']
                if positions:
                    remove_index = positions[-1]  # Remove last occurrence
                    removed_item = self.current_order.pop(remove_index)
                    self.total_price -= removed_item['price']
                    
                    self.update_order_display()
                    self.log_conversation(f"Removed {selected_item_name} from order")
                    
                    if self.voice_enabled:
                        response = f"I've removed {selected_item_name} from your order. Your new total is ${self.total_price:.2f}."
                        threading.Thread(target=lambda: self.speak(response), daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error removing item: {e}")
            messagebox.showerror("Remove Error", "Failed to remove the selected item.")

    def add_to_order_gui(self, item: str, price: float, category: str):
        """Add item to order via GUI with enhanced feedback."""
        self.current_order.append({
            "item": item,
            "price": price,
            "category": category,
            "timestamp": datetime.now()
        })
        self.total_price += price
        self.update_order_display()
        self.log_conversation(f"Added {item} to order - ${price:.2f}")
        
        # Enhanced voice confirmation
        if self.voice_enabled:
            encouragement = random.choice(self.encouragement_phrases)
            response = f"{encouragement} I've added {item} to your order for ${price:.2f}."
            threading.Thread(target=lambda: self.speak(response), daemon=True).start()

    def update_order_display(self):
        """Enhanced order display update with quantity grouping."""
        self.order_listbox.delete(0, tk.END)
        
        if not self.current_order:
            self.order_listbox.insert(tk.END, "Your order is empty")
            self.order_listbox.config(fg='#9ca3af')
        else:
            self.order_listbox.config(fg='#374151')
            
            # Group items by name for better display
            item_counts = {}
            for order_item in self.current_order:
                item_name = order_item['item']
                item_price = order_item['price']
                if item_name in item_counts:
                    item_counts[item_name]['count'] += 1
                    item_counts[item_name]['total_price'] += item_price
                else:
                    item_counts[item_name] = {
                        'count': 1,
                        'price': item_price,
                        'total_price': item_price
                    }
            
            # Display grouped items
            for i, (item_name, details) in enumerate(item_counts.items(), 1):
                count = details['count']
                total_price = details['total_price']
                
                if count == 1:
                    display_text = f"{i}. {item_name} - ${total_price:.2f}"
                else:
                    display_text = f"{i}. {item_name} (x{count}) - ${total_price:.2f}"
                
                self.order_listbox.insert(tk.END, display_text)
        
        self.total_label.config(text=f"Total: ${self.total_price:.2f}")
        
        # Update header status
        if len(self.current_order) > 0:
            self.header_status.config(text=f"● {len(self.current_order)} items", fg='#3b82f6')
        else:
            self.header_status.config(text="● Ready", fg='#22c55e')

    def clear_order(self):
        """Clear order with confirmation."""
        if not self.current_order:
            return
            
        if messagebox.askyesno("Clear Order", "Are you sure you want to clear your entire order?"):
            self.current_order = []
            self.total_price = 0.0
            self.conversation_context = {
                "stage": "ordering",
                "last_item": None,
                "suggested_items": [],
                "customer_preferences": [],
                "order_count": 0
            }
            self.update_order_display()
            self.log_conversation("Order cleared")
            
            if self.voice_enabled:
                threading.Thread(target=lambda: self.speak("Your order has been cleared. What would you like to start with?"), daemon=True).start()

    def checkout(self):
        """Enhanced checkout process."""
        if not self.current_order:
            messagebox.showwarning("Empty Order", "Please add items to your order first!")
            return
        
        # Create detailed order summary
        order_summary = "Order Summary:\n" + "="*40 + "\n"
        categories = {}
        
        for item in self.current_order:
            category = item['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        for category, items in categories.items():
            order_summary += f"\n{category.upper()}:\n"
            for item in items:
                order_summary += f"  • {item['item']} - ${item['price']:.2f}\n"
        
        order_summary += f"\n{'='*40}\n"
        order_summary += f"Total: ${self.total_price:.2f}\n"
        order_summary += f"Items: {len(self.current_order)}"
        
        result = messagebox.askyesno("Confirm Order", 
                                   f"{order_summary}\n\nWould you like to place this order?")
        
        if result:
            self.process_final_order()

    def process_final_order(self):
        """Process the final order."""
        self.log_conversation(f"🎉 Order confirmed! Total: ${self.total_price:.2f}")
        
        if self.voice_enabled:
            final_message = (f"Wonderful! Thank you so much for your order. "
                           f"Your total comes to ${self.total_price:.2f}. "
                           f"We'll have your delicious food ready shortly. "
                           f"Thanks for choosing Joe's Restaurant!")
            threading.Thread(target=lambda: self.speak(final_message), daemon=True).start()
        
        # Save order
        self.save_enhanced_order()
        
        messagebox.showinfo("Order Confirmed", 
                          "Thank you! Your order has been sent to our kitchen.\n"
                          "We'll have it ready for you shortly!")
        
        # Reset for next customer
        self.clear_order()
        self.conversation_context["stage"] = "greeting"

    def save_enhanced_order(self):
        """Save order with enhanced details."""
        try:
            order_data = {
                "order_id": f"JOE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "items": self.current_order,
                "total": self.total_price,
                "item_count": len(self.current_order),
                "customer_name": self.customer_name,
                "order_method": "voice_and_touch"
            }
            
            os.makedirs("orders", exist_ok=True)
            filename = f"orders/order_{order_data['order_id']}.json"
            
            with open(filename, 'w') as f:
                json.dump(order_data, f, indent=2, default=str)
            
            self.log_conversation(f"📄 Order saved: {order_data['order_id']}")
            
        except Exception as e:
            logger.error(f"Error saving order: {e}")

    def log_conversation(self, message: str):
        """Enhanced conversation logging."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.conversation_log.insert(tk.END, formatted_message)
        self.conversation_log.see(tk.END)
        
        # Auto-scroll and limit log size
        if int(self.conversation_log.index('end-1c').split('.')[0]) > 100:
            self.conversation_log.delete('1.0', '10.0')

    def toggle_voice_ordering(self):
        """Enhanced voice ordering toggle."""
        if not self.voice_enabled:
            messagebox.showerror("Voice System Error", 
                               "Voice recognition is not available!\n"
                               "Please check your Google Cloud credentials.")
            return
            
        if self.is_listening:
            self.stop_voice_ordering()
        else:
            self.start_voice_ordering()

    def start_voice_ordering(self):
        """Enhanced voice ordering startup."""
        if not self.voice_enabled or self.is_listening:
            return
            
        self.is_listening = True
        self.voice_button.config(text="🛑 Stop Voice Assistant", bg='#ef4444')
        self.status_label.config(text="🎤 Voice assistant is active and listening...")
        self.header_status.config(text="● Listening", fg='#7c3aed')
        self.log_conversation("🎤 Voice assistant activated")
        
        # Start enhanced voice processing
        threading.Thread(target=self.enhanced_voice_loop, daemon=True).start()

    def stop_voice_ordering(self):
        """Enhanced voice ordering stop."""
        self.is_listening = False
        self.voice_button.config(text="🎤 Start Voice Assistant", bg='#16a34a')
        self.status_label.config(text="Voice assistant stopped. Ready when you are!")
        self.header_status.config(text="● Ready", fg='#22c55e')
        self.log_conversation("🛑 Voice assistant deactivated")

    def enhanced_voice_loop(self):
        """Enhanced voice processing loop with better conversation flow."""
        try:
            # Warm welcome
            if self.conversation_context["stage"] == "greeting":
                welcome_message = random.choice(self.greeting_responses)
                self.speak(welcome_message)
                self.conversation_context["stage"] = "ordering"
            
            while self.is_listening:
                self.root.after(0, lambda: self.status_label.config(text="🎤 Listening for your voice..."))
                
                # Enhanced listening
                customer_input = self.listen_enhanced()
                
                if customer_input:
                    self.root.after(0, lambda text=customer_input: self.log_conversation(f"Customer: \"{text}\""))
                    self.process_enhanced_voice_input(customer_input)
                
                if not self.is_listening:
                    break
                    
                time.sleep(0.5)  # Brief pause between listening cycles
                    
        except Exception as e:
            logger.error(f"Enhanced voice ordering error: {e}")
            self.root.after(0, lambda: self.status_label.config(text="❌ Voice system encountered an error"))

    def process_enhanced_voice_input(self, text: str):
        """Process voice input with GPT-enhanced natural conversation."""
        text_lower = text.lower().strip()
        
        # Use GPT for better understanding if available
        if self.gpt_enabled:
            self.process_with_gpt(text)
        else:
            # Fallback to original processing
            self.process_original_input(text_lower)

    def process_with_gpt(self, text: str):
        """Process customer input using GPT for better understanding."""
        try:
            # Check if GPT client is available
            if not self.openai_client:
                logger.error("OpenAI client not initialized")
                self.process_original_input(text.lower())
                return
                
            # Prepare current order context
            current_order_text = self.get_current_order_text()
            menu_text = self.get_menu_text()
            
            # Create comprehensive prompt for GPT
            system_prompt = f"""You are Joe's Restaurant's smart ordering assistant. You help customers place, modify, and manage their food orders using natural language.

CURRENT MENU:
{menu_text}

CUSTOMER'S CURRENT ORDER:
{current_order_text}

INSTRUCTIONS:
- Understand the customer's intent (add items, remove items, modify order, get recommendations, finish order)
- Handle quantities naturally (one, two, three, etc.)
- Handle modifications like "remove the coca-cola", "cancel my burger", "delete the fries"
- Respond with a JSON object containing your understanding

RESPONSE FORMAT (JSON only):
{{
  "action": "add|remove|modify|recommend|checkout|clarify",
  "items": [
    {{
      "name": "exact menu item name",
      "quantity": number,
      "price": price from menu
    }}
  ],
  "remove_items": ["exact item names to remove"],
  "response": "friendly response to customer",
  "needs_clarification": false
}}

EXAMPLES:
- "I want two burgers" → action: "add", items with quantity 2
- "Remove the coca-cola" → action: "remove", remove_items: ["Coca-Cola"]
- "Cancel my fries" → action: "remove", remove_items: ["Crispy French Fries"]
- "What do you recommend?" → action: "recommend"
- "I'm done" → action: "checkout"

Be friendly, natural, and handle edge cases gracefully."""

            # Try available models in order of preference
            models_to_try = self.available_models if self.available_models else ["gpt-3.5-turbo"]
            
            for model in models_to_try:
                try:
                    # Make GPT API call using the modern client
                    response = self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    # Parse GPT response
                    gpt_response = response.choices[0].message.content.strip()
                    self.handle_gpt_response(gpt_response, text)
                    
                    # Log successful model used
                    logger.info(f"Successfully used model: {model}")
                    return
                    
                except Exception as model_error:
                    logger.warning(f"Model {model} failed: {str(model_error)}")
                    continue
            
            # If all models failed, use fallback
            logger.error("All GPT models failed, using fallback processing")
            self.process_original_input(text.lower())
            
        except Exception as e:
            logger.error(f"GPT processing error: {e}")
            # Fallback to original processing
            self.process_original_input(text.lower())

    def handle_gpt_response(self, gpt_response: str, original_text: str):
        """Handle the structured response from GPT."""
        try:
            # Parse JSON response
            response_data = json.loads(gpt_response)
            action = response_data.get("action", "clarify")
            
            if action == "add":
                self.handle_gpt_add_items(response_data)
            elif action == "remove":
                self.handle_gpt_remove_items(response_data)
            elif action == "modify":
                self.handle_gpt_modify_items(response_data)
            elif action == "recommend":
                self.provide_recommendations()
            elif action == "checkout":
                self.handle_order_completion()
            else:
                # Clarification needed
                response_text = response_data.get("response", "I didn't understand that clearly. Could you please repeat?")
                self.speak(response_text)
                self.root.after(0, lambda: self.log_conversation(f"AI: {response_text}"))
                
        except json.JSONDecodeError:
            logger.error("Failed to parse GPT JSON response")
            # Fallback to original processing
            self.process_original_input(original_text.lower())

    def handle_gpt_add_items(self, response_data: dict):
        """Handle adding items identified by GPT."""
        items = response_data.get("items", [])
        total_added = 0.0
        added_descriptions = []
        
        for item_data in items:
            item_name = item_data["name"]
            quantity = item_data["quantity"]
            price = item_data["price"]
            
            # Add items to order
            for _ in range(quantity):
                self.current_order.append({
                    "item": item_name,
                    "price": price,
                    "category": self.find_item_category(item_name),
                    "timestamp": datetime.now()
                })
                self.total_price += price
            
            total_added += price * quantity
            
            # Create description
            if quantity == 1:
                added_descriptions.append(item_name)
            else:
                added_descriptions.append(f"{quantity} {item_name}s" if not item_name.endswith('s') else f"{quantity} {item_name}")
        
        self.root.after(0, self.update_order_display)
        
        # Use GPT's response or create our own
        if "response" in response_data:
            response_text = response_data["response"]
        else:
            encouragement = random.choice(self.encouragement_phrases)
            items_text = ", ".join(added_descriptions)
            response_text = f"{encouragement} I've added {items_text} for ${total_added:.2f} to your order. {random.choice(self.transition_phrases)}"
        
        self.speak(response_text)
        self.root.after(0, lambda: self.log_conversation(f"AI: {response_text}"))

    def handle_gpt_remove_items(self, response_data: dict):
        """Handle removing items identified by GPT."""
        remove_items = response_data.get("remove_items", [])
        removed_descriptions = []
        total_removed = 0.0
        
        for item_name in remove_items:
            # Find and remove the item from current order
            removed_count = 0
            for i in range(len(self.current_order) - 1, -1, -1):
                if self.current_order[i]["item"].lower() == item_name.lower():
                    removed_item = self.current_order.pop(i)
                    self.total_price -= removed_item["price"]
                    total_removed += removed_item["price"]
                    removed_count += 1
                    break  # Remove only one instance
            
            if removed_count > 0:
                removed_descriptions.append(f"{item_name}")
        
        self.root.after(0, self.update_order_display)
        
        if removed_descriptions:
            items_text = ", ".join(removed_descriptions)
            response_text = response_data.get("response", f"Got it! I've removed {items_text} from your order. Your new total is ${self.total_price:.2f}. What else can I help you with?")
        else:
            response_text = "I couldn't find that item in your current order. Could you please check your order and try again?"
        
        self.speak(response_text)
        self.root.after(0, lambda: self.log_conversation(f"AI: {response_text}"))

    def handle_gpt_modify_items(self, response_data: dict):
        """Handle modifying items identified by GPT."""
        # Handle both removal and addition for modifications
        if "remove_items" in response_data:
            self.handle_gpt_remove_items(response_data)
        if "items" in response_data:
            self.handle_gpt_add_items(response_data)

    def get_current_order_text(self) -> str:
        """Get current order as text for GPT context."""
        if not self.current_order:
            return "No items in order yet."
        
        # Group items for better display
        item_counts = {}
        for order_item in self.current_order:
            item_name = order_item['item']
            if item_name in item_counts:
                item_counts[item_name]['count'] += 1
                item_counts[item_name]['total_price'] += order_item['price']
            else:
                item_counts[item_name] = {
                    'count': 1,
                    'price': order_item['price'],
                    'total_price': order_item['price']
                }
        
        order_text = []
        for item_name, details in item_counts.items():
            if details['count'] == 1:
                order_text.append(f"- {item_name} (${details['total_price']:.2f})")
            else:
                order_text.append(f"- {item_name} x{details['count']} (${details['total_price']:.2f})")
        
        return "\n".join(order_text) + f"\nTotal: ${self.total_price:.2f}"

    def get_menu_text(self) -> str:
        """Get menu as text for GPT context."""
        menu_text = []
        for category, items in self.menu.items():
            menu_text.append(f"\n{category}:")
            for item, details in items.items():
                menu_text.append(f"- {item}: ${details['price']:.2f}")
        
        return "\n".join(menu_text)

    def find_item_category(self, item_name: str) -> str:
        """Find which category an item belongs to."""
        for category, items in self.menu.items():
            for item, details in items.items():
                if item.lower() == item_name.lower():
                    return category.split()[1].lower()  # Remove emoji
        return "unknown"

    def process_original_input(self, text_lower: str):
        """Original processing method as fallback."""
        # Handle different conversation contexts
        if any(word in text_lower for word in self.done_words):
            self.handle_order_completion()
            return
        
        if any(word in text_lower for word in self.help_words):
            self.provide_recommendations()
            return
        
        if any(word in text_lower for word in self.negative_words) and self.conversation_context["last_item"]:
            self.handle_item_rejection()
            return
        
        # Try to find and add menu items
        found_items = self.find_multiple_menu_items(text_lower)
        
        if found_items:
            self.handle_found_items(found_items)
        else:
            self.handle_unclear_input(text_lower)

    def extract_quantity_and_item(self, text: str) -> List[Tuple[str, int, float, str]]:
        """Extract quantity and menu items from customer's speech."""
        found_items = []
        text_words = text.lower().split()
        
        # Search through all menu items
        for category, items in self.menu.items():
            category_clean = category.split()[1].lower()  # Remove emoji
            
            for item, details in items.items():
                item_words = item.lower().split()
                quantity = 1  # Default quantity
                
                # Look for quantity indicators before the item
                for i, word in enumerate(text_words):
                    if word in self.number_words:
                        # Check if the next words match this item
                        remaining_text = " ".join(text_words[i+1:])
                        if self.item_matches_text(item, remaining_text):
                            quantity = self.number_words[word]
                            found_items.append((item, quantity, details['price'], category_clean))
                            break
                
                # Also check for items without explicit quantity (default to 1)
                if not any(item_tuple[0] == item for item_tuple in found_items):
                    if self.item_matches_text(item, text):
                        # Check for synonyms and partial matching
                        if self.check_synonyms_and_partials(text, item, details['price'], category_clean):
                            found_items.append((item, 1, details['price'], category_clean))
                        else:
                            # Exact match scoring
                            exact_matches = sum(1 for word in item_words if word in text)
                            if exact_matches >= len(item_words) / 2:  # At least half the words match
                                found_items.append((item, 1, details['price'], category_clean))
        
        return found_items

    def item_matches_text(self, item: str, text: str) -> bool:
        """Check if an item matches the text."""
        item_words = item.lower().split()
        text_lower = text.lower()
        
        # Check if all important words of the item are in the text
        matches = sum(1 for word in item_words if len(word) > 2 and word in text_lower)
        return matches >= max(1, len(item_words) // 2)

    def find_multiple_menu_items(self, text: str) -> List[Tuple[str, int, float, str]]:
        """Find multiple menu items with quantities from customer's speech."""
        return self.extract_quantity_and_item(text)

    def check_synonyms_and_partials(self, text: str, item: str, price: float, category: str) -> bool:
        """Check for synonyms and partial matches."""
        # Enhanced synonyms dictionary
        synonyms = {
            "coke": "cola", "pepsi": "cola", "soda": "cola", "soft drink": "cola",
            "fries": "french fries", "chips": "french fries", "potatoes": "french fries",
            "shake": "milkshake", "milk shake": "milkshake",
            "burger": "burger", "sandwich": "burger",
            "rings": "onion rings", "onions": "onion rings",
            "water": "bottled water", "h2o": "bottled water",
            "coffee": "premium coffee", "java": "premium coffee",
            "salad": "side salad", "greens": "side salad",
            "cake": "chocolate cake", "dessert": "cake",
            "ice cream": "vanilla ice cream", "frozen": "ice cream"
        }
        
        item_lower = item.lower()
        
        for synonym, target in synonyms.items():
            if synonym in text and target in item_lower:
                return True
        
        return False

    def handle_found_items(self, found_items: List[Tuple[str, int, float, str]]):
        """Handle when menu items are found in customer speech with quantities."""
        total_items_added = 0
        total_price_added = 0.0
        added_descriptions = []
        
        for item, quantity, price, category in found_items:
            # Add the specified quantity of this item
            for _ in range(quantity):
                self.current_order.append({
                    "item": item,
                    "price": price,
                    "category": category,
                    "timestamp": datetime.now()
                })
                self.total_price += price
                total_items_added += 1
            
            total_price_added += price * quantity
            self.conversation_context["last_item"] = item
            self.conversation_context["order_count"] += quantity
            
            # Create description for this item
            if quantity == 1:
                added_descriptions.append(f"{item}")
            else:
                added_descriptions.append(f"{quantity} {item}s" if not item.endswith('s') else f"{quantity} {item}")
        
        self.root.after(0, self.update_order_display)
        
        # Enhanced response based on number of items and quantities
        if len(found_items) == 1:
            item, quantity, price, _ = found_items[0]
            encouragement = random.choice(self.encouragement_phrases)
            transition = random.choice(self.transition_phrases)
            
            if quantity == 1:
                response = f"{encouragement} I've added {item} for ${price:.2f} to your order. {transition}"
            else:
                total_for_item = price * quantity
                response = f"{encouragement} I've added {quantity} {item}s for ${total_for_item:.2f} to your order. {transition}"
        else:
            items_text = ", ".join(added_descriptions)
            response = f"Perfect! I've added {items_text} to your order for ${total_price_added:.2f}. What else would you like?"
        
        self.speak(response)
        self.root.after(0, lambda: self.log_conversation(f"AI: {response}"))

    def handle_order_completion(self):
        """Handle when customer wants to finish ordering."""
        if not self.current_order:
            response = "I don't see any items in your order yet. What would you like to start with?"
        else:
            item_count = len(self.current_order)
            response = (f"Perfect! You have {item_count} item{'s' if item_count != 1 else ''} "
                       f"for a total of ${self.total_price:.2f}. Let me process your order now.")
        
        self.speak(response)
        self.root.after(0, lambda: self.log_conversation(f"AI: {response}"))
        
        if self.current_order:
            time.sleep(2)  # Brief pause
            self.root.after(0, self.checkout)

    def provide_recommendations(self):
        """Provide intelligent recommendations with quantity examples."""
        recommendations = [
            "Our Joe's Classic Burger is a customer favorite! You could say 'I want one classic burger' or 'give me two classic burgers.'",
            "The BBQ Bacon Deluxe is absolutely delicious! Try saying 'I'll have one BBQ bacon deluxe.'",
            "Many customers love our Crispy French Fries with their burger! You can order by saying 'add two fries' or 'I want three orders of fries.'",
            "The Creamy Milkshake is perfect to go with any meal! Just say 'one milkshake' or 'give me two chocolate milkshakes.'",
            "Our Triple Chocolate Cake is amazing if you have room for dessert! Try 'I want one chocolate cake' or 'two slices of cake please.'"
        ]
        
        # Contextual recommendations
        if not self.current_order:
            response = "For first-time visitors, I highly recommend our Joe's Classic Burger - just say 'I want one classic burger!' Or if you prefer chicken, try 'give me one grilled chicken supreme.' You can always specify quantities like 'two burgers' or 'three drinks.'"
        elif any("burger" in item["item"].lower() for item in self.current_order):
            response = "Great burger choice! How about adding some sides? You could say 'add two orders of fries' or 'I want three onion rings' to go with that!"
        else:
            response = random.choice(recommendations)
        
        self.speak(response)
        self.root.after(0, lambda: self.log_conversation(f"AI: {response}"))

    def handle_item_rejection(self):
        """Handle when customer doesn't want the last suggested item."""
        response = "No problem at all! What else can I help you find on our menu?"
        self.speak(response)
        self.root.after(0, lambda: self.log_conversation(f"AI: {response}"))

    def handle_unclear_input(self, text: str):
        """Handle unclear or unrecognized input with helpful responses."""
        unclear_responses = [
            "I want to make sure I get your order right. Try saying something like 'I want two burgers' or 'give me one ice cream.' What would you like from our menu?",
            "I didn't catch that clearly. You can say things like 'three fries' or 'one chocolate cake.' What specific item would you like to order?",
            "Let me help you find what you're looking for. Try being specific with quantities - say 'two milkshakes' or 'one classic burger.' What sounds good to you?",
            "Could you repeat that? Remember, you can specify quantities like 'I'll have three sodas' or 'give me two salads.' What would you like to add to your order?"
        ]
        
        response = random.choice(unclear_responses)
        self.speak(response)
        self.root.after(0, lambda: self.log_conversation(f"AI: {response}"))

    def speak(self, text: str):
        """Enhanced text-to-speech with more natural voice."""
        try:
            if not self.voice_enabled:
                return
                
            # Get TTS settings from config
            voice_name = getattr(config, 'TTS_VOICE_NAME', 'en-US-Neural2-F') if CONFIG_LOADED else 'en-US-Neural2-F'
            speaking_rate = getattr(config, 'TTS_SPEAKING_RATE', 0.95) if CONFIG_LOADED else 0.95
            language_code = getattr(config, 'TTS_LANGUAGE_CODE', 'en-US') if CONFIG_LOADED else 'en-US'
                
            # Enhanced synthesis settings
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                name=voice_name
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=0.0,
                volume_gain_db=0.0
            )
            
            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            # Save and play audio
            temp_file = "temp_voice.mp3"
            with open(temp_file, "wb") as out:
                out.write(response.audio_content)
            
            # Platform-specific audio playback
            if platform.system() == "Darwin":  # macOS
                os.system(f"afplay {temp_file}")
            elif platform.system() == "Windows":
                os.system(f"start {temp_file}")
            else:  # Linux
                os.system(f"mpg123 {temp_file}")
            
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            logger.error(f"Enhanced text-to-speech error: {e}")

    def listen_enhanced(self) -> Optional[str]:
        """Enhanced audio recording and transcription."""
        try:
            # Get audio settings from config
            chunk_size = getattr(config, 'AUDIO_CHUNK_SIZE', 4096) if CONFIG_LOADED else 4096
            sample_rate = getattr(config, 'AUDIO_SAMPLE_RATE', 16000) if CONFIG_LOADED else 16000
            record_seconds = getattr(config, 'AUDIO_RECORD_SECONDS', 5) if CONFIG_LOADED else 5
            confidence_threshold = getattr(config, 'CONFIDENCE_THRESHOLD', 0.7) if CONFIG_LOADED else 0.7
            
            # Enhanced recording parameters
            CHUNK = chunk_size
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = sample_rate
            RECORD_SECONDS = record_seconds
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, 
                          channels=CHANNELS, 
                          rate=RATE, 
                          input=True, 
                          frames_per_buffer=CHUNK)
            
            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                if not self.is_listening:
                    break
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save enhanced audio file
            temp_wav = "temp_enhanced.wav"
            with wave.open(temp_wav, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            
            # Enhanced transcription
            with open(temp_wav, "rb") as f:
                content = f.read()
            
            audio = speech.RecognitionAudio(content=content)
            config_obj = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code="en-US",
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True,
                model="latest_long",  # Better model for restaurant context
                use_enhanced=True
            )
            
            response = self.speech_client.recognize(config=config_obj, audio=audio)
            
            # Cleanup
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                
                # Only return high-confidence results
                if confidence > confidence_threshold:
                    return transcript
                    
            return None
            
        except Exception as e:
            logger.error(f"Enhanced speech recognition error: {e}")
            return None

def main():
    """Launch the professional restaurant ordering system."""
    try:
        root = tk.Tk()
        app = VoiceRestaurantGUI(root)
        
        # Show detailed GPT integration status
        if not app.gpt_enabled:
            messagebox.showinfo("GPT Integration", 
                              "GPT integration is disabled. To enable advanced natural language understanding:\n\n"
                              "1. Get an OpenAI API key from https://platform.openai.com/\n"
                              "2. Replace the API key in the code\n"
                              "3. Install openai package: pip install openai>=1.0\n\n"
                              "The system will work with basic voice recognition without GPT.")
        elif app.available_models:
            model_info = f"🎉 GPT Integration Active!\n\nUsing: {app.available_models[0].upper()}\nAll available: {', '.join(app.available_models)}\n\nAdvanced Commands Now Work:\n• 'Remove the coca-cola'\n• 'Cancel my burger'\n• 'Change fries to onion rings'\n• 'Delete everything and start over'"
            messagebox.showinfo("GPT Integration Success", model_info)
        else:
            messagebox.showwarning("GPT Setup Issue", 
                                  f"OpenAI connection established but no compatible models found.\n\n"
                                  f"This might mean:\n"
                                  f"• Your API key doesn't have access to GPT models\n"
                                  f"• You need to add credits to your OpenAI account\n"
                                  f"• API rate limits are active\n\n"
                                  f"The system will use basic voice recognition instead.")
        
        # Center window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (root.winfo_screenheight() // 2) - (900 // 2)
        root.geometry(f"1400x900+{x}+{y}")
        
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Application startup error: {e}")
        messagebox.showerror("Startup Error", 
                           f"Failed to start the application: {str(e)}")

if __name__ == "__main__":
    main()