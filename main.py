import customtkinter as ctk
import os, json, logging
from threading import Thread
from coomer_uploader import logging_setup
import sys

logging_setup.setup_logger(log_to_file=True)
logger = logging.getLogger(__name__)

from coomer_uploader import gofile, bunkr, pixeldrain

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Coomer Uploader")
        self.geometry("400x520")
        self.resizable(False, False)
        self.bunkr_config_file="bunkr_config.json"
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)    
        self.main_container = ctk.CTkFrame(self, fg_color="transparent") 
        self.main_container.grid(column=0, row=0,padx=10, pady=10, sticky="nw")
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=1)
        self.main_container.rowconfigure(0, weight=1)

        self.upper_container = ctk.CTkFrame(self.main_container)
        self.upper_container.grid(column=0, row=0,padx=10, pady=10, sticky="nwse")
        self.upper_container.columnconfigure(0, weight=1)
        self.upper_container.columnconfigure(1, weight=1)
        self.upper_container.rowconfigure(0, weight=1)
        
        self.lower_container = ctk.CTkFrame(self.main_container)
        self.lower_container.grid(column=0, row=1, padx=10, pady=(0, 0), sticky="nwse")
        self.lower_container.columnconfigure(0, weight=0)
        self.lower_container.columnconfigure(1, weight=1)
        self.lower_container.rowconfigure(0, weight=1)

        self.footer_container = ctk.CTkFrame(self.main_container)
        self.footer_container.grid(column=0, row=3,padx=10, pady=0, sticky="nwse")
        self.footer_container.columnconfigure(0, weight=1)
        self.footer_container.columnconfigure(1, weight=1)
        self.footer_container.rowconfigure(0, weight=1)

        self.selected_hosts = []
        self.build_host_selection_section()
        self.build_file_selection_section()
        self.build_album_name_section()
        self.build_bunkr_settings_section()
        self.build_links_section()
        self.build_console_output_section()        
        logging.getLogger().addHandler(self.create_handler())
        
        self.get_bunkr_settings()
        
    def build_console_output_section(self):
        self.show_console_button = ctk.CTkButton(self.footer_container, text="Show console", command=self.toggle_flyout)
        self.show_console_button.grid(column=0, row=0, padx=10, pady=(10, 10),columnspan=4,sticky='nsew')

        self.flyout_frame = ctk.CTkFrame(self, fg_color="black", corner_radius=10)
        self.flyout_frame.configure(width=450, height=self.winfo_height()-30)
        self.flyout_frame.place_forget()

        self.initial_width = self.winfo_width()
        self.initial_height = self.winfo_height()

        self.console_output = ctk.CTkTextbox(self.flyout_frame, fg_color="transparent", font=(None,10), height=self.winfo_height()-30, width=600)
        self.console_output.grid(column=0, row=0, padx=10, sticky="nsew")

    def toggle_flyout(self):
        if self.flyout_frame.winfo_ismapped():  
            self.flyout_frame.place_forget() 
            self.geometry(f"{self.initial_width}x{self.initial_height}")
            self.show_console_button.configure(text='Show console')
            
        else:
            button_x = 40
            button_y = 20
            button_width = self.upper_container.winfo_width()
            self.show_console_button.configure(text='Hide console')
            new_width = self.initial_width + self.flyout_frame.winfo_reqwidth()
            self.geometry(f"{new_width}x{self.initial_height}")
            self.flyout_frame.place(x=button_x + button_width, y=button_y)
            self.flyout_frame.tkraise()

    def build_host_selection_section(self):
        self.hosts_frame = ctk.CTkFrame(self.upper_container)
        self.hosts_frame.grid(column=0, row=0, padx=10, pady=10, sticky="nswe",columnspan=3)
        self.hosts_frame.columnconfigure(0, weight=1)
        self.hosts_frame.columnconfigure(1, weight=1)
        self.hosts_frame.rowconfigure(0, weight=1)

        self.hosts_label = ctk.CTkLabel(self.hosts_frame, text="Hosts")
        self.hosts_label.grid(column=0, row=0, sticky="nswe")

        self.gofile_checkbox = ctk.CTkCheckBox(
            self.hosts_frame,
            text="Gofile",
            command=lambda: self.add_remove_host("gofile", self.gofile_checkbox)
        )
        self.gofile_checkbox.grid(column=0, row=1, padx=(10, 0), pady=(0, 10))

        self.bunkr_checkbox = ctk.CTkCheckBox(
            self.hosts_frame,
            text="Bunkr",
            command=lambda: self.add_remove_host("bunkr", self.bunkr_checkbox)
        )
        self.bunkr_checkbox.grid(column=0, row=2, padx=(10, 0), pady=(0, 10))  
        
        self.pixeldrain_checkbox = ctk.CTkCheckBox(
            self.hosts_frame,
            text="Pixeldrain",
            command=lambda: self.add_remove_host("pixeldrain", self.pixeldrain_checkbox)
        )
        self.pixeldrain_checkbox.grid(column=0, row=3, padx=(10, 0), pady=(0, 10))  
       
    def build_album_name_section(self):
        self.album_name_frame = ctk.CTkFrame(self.upper_container)
        self.album_name_frame.grid(column=0, row=1, padx=10, pady=10,columnspan=6)
        self.album_name_frame.columnconfigure(1, weight=1)
        self.album_name_frame.rowconfigure(2, weight=1)

        self.album_name_label = ctk.CTkLabel(self.album_name_frame, text="Album name (required, applies to all hosts)")
        self.album_name_label.grid(column=2, row=0, padx=10, pady=(0, 10), sticky="nswe",columnspan=3)
        self.album_entry = ctk.CTkEntry(
           self.album_name_frame,
            placeholder_text="Album Name",
            justify="center"
        )
        self.album_entry.grid(column=2, row=1, padx=10, pady=(0, 10), sticky="nwse",columnspan=4)

    def build_file_selection_section (self):
        self.upload_frame = ctk.CTkFrame(self.upper_container)
        self.upload_frame.grid(column=3, row=0, padx=(0, 10), pady=10, sticky="nsw",columnspan=3)
        
        self.progressbar = ctk.CTkProgressBar(
            self.upload_frame,
            width=140,
            mode="indeterminate"
        )
        self.progressbar.set(0)
        self.progressbar.grid(column=0, row=4, padx=10, pady=(0, 15))
        
        self.upload_label = ctk.CTkLabel(self.upload_frame, text="Upload")
        self.upload_label.grid(column=0, row=0)
         
        self.select_files_button = ctk.CTkButton(
            self.upload_frame,
            text="Files",
            command=self.select_files
        )
        self.select_files_button.grid(column=0, row=2, padx=10, pady=(0, 10))
        
        self.upload_button_text = ctk.StringVar()
        self.upload_button_text.set('Upload')
        self.upload_button = ctk.CTkButton(
            self.upload_frame,
            textvariable=self.upload_button_text,
            state="disabled",
            command=lambda: Thread(target=self.upload_callback).start()
        )
        self.upload_button.grid(column=0, row=3, padx=10, pady=(0, 10))
        
    def build_bunkr_settings_section(self):
        self.bunkr_frame = ctk.CTkFrame(self.lower_container)
        self.bunkr_frame.grid(column=0, row=0, padx=10, pady=10,  sticky="nws",columnspan=3)
        
        self.bunkr_label = ctk.CTkLabel(self.bunkr_frame, text="Bunkr Settings")
        self.bunkr_label.grid(column=0, row=0)
        
        self.token_entry = ctk.CTkEntry(
            self.bunkr_frame,
            placeholder_text="Token",
            justify="center"
        )
        self.token_entry.grid(column=0, row=2, padx=10, pady=(0, 10), sticky="n")

        self.cookies_entry = ctk.CTkEntry(
            self.bunkr_frame,
            placeholder_text="Cookies",
            justify="center"
        )
        self.cookies_entry.grid(column=0, row=3, padx=10, pady=(0, 10), sticky="n")
        
        self.token_save_button = ctk.CTkButton(
            self.bunkr_frame,
            text="Save Settings",
            command=lambda: Thread(target=self.save_bunkr_settings).start()
        )
        self.token_save_button.grid(column=0, row=5, padx=10, pady=(0, 10), sticky="swe")
        
    def build_links_section(self):

        self.links_frame = ctk.CTkFrame(self.lower_container)
        self.links_frame.grid(column=3, row=0, padx=(0,10), pady=10, sticky="nsw",columnspan=5)
        
        self.links_label = ctk.CTkLabel(self.links_frame, text="Links")
        self.links_label.grid(column=0, row=0, sticky="nwse")
        
        self.links_box = ctk.CTkTextbox(
            self.links_frame,
            width=70,
            height=90,
        )
        self.links_box.grid(column=0, row=2, padx=(10,10), pady=(0,10), sticky="nswe")
        
        self.copy_links_button = ctk.CTkButton(
            self.links_frame,
            text="Copy Links",
            command=self.copy_links_callback
        )
        self.copy_links_button.grid(column=0, row=4, padx=(10,10), pady=(0, 10), sticky="ns")
    
    def save_bunkr_settings(self):
        if len(self.token_entry.get()) == 0:
            return
        
        if len(self.cookies_entry.get()) == 0:
            return

        data = {'token': self.token_entry.get(), 'cookies': json.loads(self.cookies_entry.get().strip()) }
        
        with open(self.bunkr_config_file, 'w') as f:
            json.dump(data, f)
            
        self.get_bunkr_settings()
            
    def get_bunkr_settings(self):
        if not os.path.isfile(self.bunkr_config_file):
            self.bunkr_checkbox.configure(state='disabled')
            return
        
        with open(self.bunkr_config_file, 'r') as f:
            _=json.load(f)
            self.bunkr_token = _['token']
            self.bunkr_cookies = _['cookies']
        
        self.token_entry.insert("0", self.bunkr_token)
        self.cookies_entry.insert("0", self.bunkr_cookies)
        self.bunkr_checkbox.configure(state='normal')
    
    def copy_links_callback(self):
        self.clipboard_clear()
        self.clipboard_append(self.links_box.get("1.0", "end"))
        #self.links_box.delete("1.0", "end")
      
    def add_remove_host(self, host, checkbox):
        if checkbox.get() == 0:
            try:
                self.selected_hosts.remove(host)
            except:
                return
        else:
            self.selected_hosts.append(host)
    
    def select_files(self):
        self.upload_button_text.set('Upload')
        self.files = ctk.filedialog.askopenfilenames()
        
        if len(self.files) == 0:
            return
        
        self.select_files_button.configure(text=f"{len(self.files)} files selected")
        self.upload_button.configure(state="normal")
                
    def upload_callback(self):
        self.upload_button.configure(state='disabled')
        t = Thread(target=self.upload_files)
        t.start()
        t.join()
        
    def upload_files(self):
        if not self.selected_hosts:
            self.upload_button_status("No host selected!", 'normal')
            self.select_files_button.configure(text='Select')
            return
        
        self.progressbar.start()
        self.links_box.delete("1.0", "end")
        
        if len(self.album_entry.get()) == 0:
            self.upload_button_status("Album name missing!", 'normal')
            self.select_files_button.configure(text="Select")
            self.progressbar.stop()
            return
        
        if "gofile" in self.selected_hosts:
            self.upload_button_status("Gofile...", 'disabled')
            
            try:
                gofile_conn= gofile()
                url=gofile_conn.upload_files(self.files,self.album_entry.get())
                self.links_box.insert("end", f"{url}\n")
                self.upload_button_status("Gofile completed!", 'normal')

            except Exception as e:
                logger.exception(e)
                self.upload_button_status("Gofile failed!", 'normal')
          
  
        if "pixeldrain" in self.selected_hosts:
            self.upload_button_status("Pixeldrain...", 'disabled')
            
            try:
                pixeldrain_conn= pixeldrain()
                url = url=pixeldrain_conn.upload_files(self.files,self.album_entry.get())
                self.links_box.insert("end", f"{url}\n")
                self.upload_button_status("Pixeldrain completed!", 'normal')
            except Exception as e:
                logger.error(e)
                self.upload_button_status("Pixeldrain failed!", 'normal')

        if "bunkr" in self.selected_hosts:
            self.upload_button_status("Bunkr...", 'disabled')
            
            try:
                bunkr_conn= bunkr(self.bunkr_token, self.bunkr_cookies)
                url=bunkr_conn.upload_files(self.files,self.album_entry.get())
                self.links_box.insert("end", f"{url}\n")
                self.upload_button_status("Bunkr completed!", 'normal')

            except Exception as e:
                logger.error(e)
                self.upload_button_status("Bunkr failed!", 'normal')
                raise e
            
        logger.info('DONE')
        self.progressbar.stop()
        self.select_files_button.configure(text="Select")
        
    def upload_button_status(self, text, select_state):
        self.upload_button_text.set(text)
        self.select_files_button.configure(state = select_state)
        
    def check_conditions(self):
        if len(self.album_entry.get()) == 0:
            self.upload_button_status("Album name missing!", 'normal')
            self.upload_button.configure(state='normal')
            return
        
    def create_handler(self):
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO) 
        
        def update_label(record):
            self.console_output.insert("end", f"[{record.name.split('.')[-1]}] {record.getMessage()}\n")
            self.console_output.see("end")

        handler.emit = update_label 
        return handler

if __name__ == "__main__":
    app = App()
    app.mainloop()