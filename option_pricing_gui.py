import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import math
import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks

class OptionPricingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Options Pricing Calculator")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Create menu bar
        self.create_menu()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        self.create_widgets()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Configuration...", command=self.save_config)
        file_menu.add_command(label="Load Configuration...", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.main_frame, text="Options Pricing Calculator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Base Parameters Section
        self.create_base_parameters_section()
        
        # Tranches Section
        self.create_tranches_section()
        
        # Control Buttons
        self.create_control_buttons()
        
        # Results Section
        self.create_results_section()
        
        # Exit Button
        self.create_exit_button()
        
    def create_base_parameters_section(self):
        # Base Parameters Frame
        base_frame = ttk.LabelFrame(self.main_frame, text="Base Parameters", padding="10")
        base_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        base_frame.columnconfigure(1, weight=1)
        base_frame.columnconfigure(3, weight=1)
        
        # Row 1: Asset Value and Total Shares
        ttk.Label(base_frame, text="Total Asset Value ($):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.asset_value_var = tk.StringVar(value="1000000")
        ttk.Entry(base_frame, textvariable=self.asset_value_var, width=15).grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Label(base_frame, text="Total Shares:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.total_shares_var = tk.StringVar(value="100000")
        ttk.Entry(base_frame, textvariable=self.total_shares_var, width=15).grid(row=0, column=3, padx=5, sticky=(tk.W, tk.E))
        
        # Row 2: Current Price (calculated) and Volatility
        ttk.Label(base_frame, text="Current Price/Token ($):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.current_price_var = tk.StringVar(value="10.00")
        self.current_price_label = ttk.Label(base_frame, textvariable=self.current_price_var, 
                                           background="white", relief="sunken", width=15)
        self.current_price_label.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(base_frame, text="Volatility (decimal):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.volatility_var = tk.StringVar(value="0.30")
        ttk.Entry(base_frame, textvariable=self.volatility_var, width=15).grid(row=1, column=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Row 3: Risk-free rate and delivery date
        ttk.Label(base_frame, text="Risk-free Rate (decimal):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.risk_free_rate_var = tk.StringVar(value="0.05")
        ttk.Entry(base_frame, textvariable=self.risk_free_rate_var, width=15).grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(base_frame, text="Delivery Date (YYYY-MM-DD):").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        future_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        self.delivery_date_var = tk.StringVar(value=future_date)
        ttk.Entry(base_frame, textvariable=self.delivery_date_var, width=15).grid(row=2, column=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Bind events to update current price
        self.asset_value_var.trace('w', self.update_current_price)
        self.total_shares_var.trace('w', self.update_current_price)
        
    def create_tranches_section(self):
        # Tranches Frame
        tranches_frame = ttk.LabelFrame(self.main_frame, text="Option Tranches", padding="10")
        tranches_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        tranches_frame.columnconfigure(0, weight=1)
        tranches_frame.rowconfigure(1, weight=1)
        
        # Control buttons for tranches
        control_frame = ttk.Frame(tranches_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="Add Tranche", command=self.add_tranche_inline).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Remove Tranche", command=self.remove_tranche).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Quick Add (Dialog)", command=self.add_tranche).pack(side=tk.LEFT, padx=5)
        
        # Tranches table
        self.create_tranches_table(tranches_frame)
        
        # Add initial tranche
        self.add_tranche_inline()
        
    def create_tranches_table(self, parent):
        # Table frame with scrollbar
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview for table
        columns = ('Entity', 'Tranche', 'Option Type', 'Strike Price', 'Number of Options')
        self.tranches_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.tranches_tree.heading('Entity', text='Entity')
        self.tranches_tree.heading('Tranche', text='Tranche #')
        self.tranches_tree.heading('Option Type', text='Type (Call/Put)')
        self.tranches_tree.heading('Strike Price', text='Strike Price ($)')
        self.tranches_tree.heading('Number of Options', text='# Options')
        
        self.tranches_tree.column('Entity', width=120, anchor=tk.CENTER)
        self.tranches_tree.column('Tranche', width=80, anchor=tk.CENTER)
        self.tranches_tree.column('Option Type', width=100, anchor=tk.CENTER)
        self.tranches_tree.column('Strike Price', width=100, anchor=tk.CENTER)
        self.tranches_tree.column('Number of Options', width=100, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tranches_tree.yview)
        self.tranches_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid treeview and scrollbar
        self.tranches_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click to edit
        self.tranches_tree.bind('<Double-1>', self.edit_tranche_inline)
        self.editing_item = None
        self.edit_entry = None
        
        self.tranche_counter = 0
        
    def create_control_buttons(self):
        # Control buttons frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Calculate Options", 
                  command=self.calculate_options, style='Accent.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=10)
        
    def create_results_section(self):
        # Results frame
        results_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results text widget with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(text_frame, height=12, wrap=tk.WORD)
        results_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_exit_button(self):
        # Exit button frame
        exit_frame = ttk.Frame(self.main_frame, padding="10")
        exit_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Exit button
        ttk.Button(exit_frame, text="Exit Application", command=self.exit_application, 
                  style='Accent.TButton').pack()
    
    def exit_application(self):
        # Close the application
        self.root.quit()
        self.root.destroy()
    
    def update_current_price(self, *args):
        try:
            asset_value = float(self.asset_value_var.get() or 0)
            total_shares = float(self.total_shares_var.get() or 1)
            current_price = asset_value / total_shares if total_shares != 0 else 0
            self.current_price_var.set(f"{current_price:.2f}")
        except ValueError:
            self.current_price_var.set("0.00")
    
    def add_tranche_inline(self):
        self.tranche_counter += 1
        default_data = ("Entity A", self.tranche_counter, "call", "12.00", "1000")
        self.tranches_tree.insert('', 'end', values=default_data)
        
    def add_tranche(self):
        self.tranche_counter += 1
        tranche_window = TrancheInputWindow(self.root, self.tranche_counter, self.add_tranche_to_table)
        
    def add_tranche_to_table(self, tranche_data):
        self.tranches_tree.insert('', 'end', values=tranche_data)
        
    def remove_tranche(self):
        selected = self.tranches_tree.selection()
        if selected:
            self.tranches_tree.delete(selected)
        else:
            messagebox.showwarning("Selection Required", "Please select a tranche to remove.")
    
    def edit_tranche_inline(self, event):
        item = self.tranches_tree.selection()[0] if self.tranches_tree.selection() else None
        if not item:
            return
            
        # Get the column clicked
        column = self.tranches_tree.identify_column(event.x)
        
        if column in ['#1', '#3', '#4', '#5']:  # Entity, Option Type, Strike Price, Number of Options
            self.start_inline_edit(item, column, event.x, event.y)
    
    def start_inline_edit(self, item, column, x, y):
        # Clean up any existing edit
        if self.edit_entry:
            self.edit_entry.destroy()
        
        self.editing_item = item
        
        # Get current value
        values = list(self.tranches_tree.item(item, 'values'))
        col_index = int(column.replace('#', '')) - 1
        current_value = values[col_index]
        
        # Get cell coordinates
        bbox = self.tranches_tree.bbox(item, column)
        if not bbox:
            return
            
        x, y, width, height = bbox
        
        if col_index == 2:  # Option Type - use combobox
            self.edit_entry = ttk.Combobox(self.tranches_tree, values=["call", "put"], state="readonly")
            self.edit_entry.set(current_value)
        else:  # Strike Price or Number of Options - use entry
            self.edit_entry = ttk.Entry(self.tranches_tree)
            self.edit_entry.insert(0, current_value)
            
        self.edit_entry.place(x=x, y=y, width=width, height=height)
        self.edit_entry.focus()
        
        # Bind events
        self.edit_entry.bind('<Return>', lambda e: self.finish_inline_edit(col_index))
        self.edit_entry.bind('<Escape>', lambda e: self.cancel_inline_edit())
        self.edit_entry.bind('<FocusOut>', lambda e: self.finish_inline_edit(col_index))
    
    def finish_inline_edit(self, col_index):
        if not self.edit_entry or not self.editing_item:
            return
            
        # Get new value
        new_value = self.edit_entry.get()
        
        # Update the item
        values = list(self.tranches_tree.item(self.editing_item, 'values'))
        values[col_index] = new_value
        self.tranches_tree.item(self.editing_item, values=values)
        
        # Clean up
        self.cancel_inline_edit()
    
    def cancel_inline_edit(self):
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
        self.editing_item = None
    
    def edit_tranche(self, event):
        selected = self.tranches_tree.selection()
        if selected:
            item = selected[0]
            values = self.tranches_tree.item(item, 'values')
            tranche_window = TrancheInputWindow(self.root, values[1], 
                                              lambda data: self.update_tranche(item, data), values)
    
    def update_tranche(self, item, data):
        self.tranches_tree.item(item, values=data)
    
    def clear_all(self):
        self.tranches_tree.delete(*self.tranches_tree.get_children())
        self.results_text.delete(1.0, tk.END)
        self.tranche_counter = 0
        
    def save_config(self):
        try:
            config = {
                'base_parameters': {
                    'asset_value': self.asset_value_var.get(),
                    'total_shares': self.total_shares_var.get(),
                    'volatility': self.volatility_var.get(),
                    'risk_free_rate': self.risk_free_rate_var.get(),
                    'delivery_date': self.delivery_date_var.get()
                },
                'tranches': []
            }
            
            # Get tranches data
            for item in self.tranches_tree.get_children():
                values = self.tranches_tree.item(item, 'values')
                config['tranches'].append({
                    'entity': values[0],
                    'tranche_num': values[1],
                    'option_type': values[2],
                    'strike_price': values[3],
                    'num_options': values[4]
                })
            
            filename = filedialog.asksaveasfilename(
                title="Save Configuration",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Success", f"Configuration saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        try:
            filename = filedialog.askopenfilename(
                title="Load Configuration",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Load base parameters
                if 'base_parameters' in config:
                    params = config['base_parameters']
                    self.asset_value_var.set(params.get('asset_value', '1000000'))
                    self.total_shares_var.set(params.get('total_shares', '100000'))
                    self.volatility_var.set(params.get('volatility', '0.30'))
                    self.risk_free_rate_var.set(params.get('risk_free_rate', '0.05'))
                    self.delivery_date_var.set(params.get('delivery_date', 
                        (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")))
                
                # Clear existing tranches
                self.tranches_tree.delete(*self.tranches_tree.get_children())
                
                # Load tranches
                if 'tranches' in config:
                    self.tranche_counter = 0
                    for tranche in config['tranches']:
                        self.tranche_counter = max(self.tranche_counter, int(tranche.get('tranche_num', 0)))
                        data = (
                            tranche.get('entity', 'Entity A'),
                            tranche.get('tranche_num', self.tranche_counter),
                            tranche.get('option_type', 'call'),
                            tranche.get('strike_price', '12.00'),
                            tranche.get('num_options', '1000')
                        )
                        self.tranches_tree.insert('', 'end', values=data)
                
                messagebox.showinfo("Success", f"Configuration loaded from {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def export_results(self):
        if not hasattr(self, 'last_results') or not self.last_results:
            messagebox.showwarning("No Results", "Please calculate options first before exporting results.")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Results",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.last_results, f, indent=2)
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
    def calculate_options(self):
        try:
            # Get base parameters
            asset_value = float(self.asset_value_var.get())
            total_shares = float(self.total_shares_var.get())
            current_price = asset_value / total_shares
            volatility = float(self.volatility_var.get())
            risk_free_rate = float(self.risk_free_rate_var.get())
            
            # Parse delivery date
            delivery_date = datetime.strptime(self.delivery_date_var.get(), "%Y-%m-%d")
            time_to_expiration = (delivery_date - datetime.now()).days / 365.25
            
            if time_to_expiration <= 0:
                messagebox.showerror("Error", "Delivery date must be in the future!")
                return
            
            # Get tranches data
            tranches = []
            for item in self.tranches_tree.get_children():
                values = self.tranches_tree.item(item, 'values')
                tranches.append({
                    'entity': values[0],
                    'tranche_num': values[1],
                    'option_type': values[2].lower(),
                    'strike_price': float(values[3]),
                    'num_options': int(values[4])
                })
            
            if not tranches:
                messagebox.showwarning("No Data", "Please add at least one tranche.")
                return
            
            # Calculate results
            self.display_results(current_price, asset_value, total_shares, volatility, 
                               risk_free_rate, time_to_expiration, delivery_date, tranches)
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Please check your inputs: {str(e)}")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error in calculation: {str(e)}")
    
    def display_results(self, current_price, asset_value, total_shares, volatility, 
                       risk_free_rate, time_to_expiration, delivery_date, tranches):
        
        self.results_text.delete(1.0, tk.END)
        
        # Base parameters
        results = f"{'='*80}\n"
        results += f"OPTION PRICING RESULTS\n"
        results += f"{'='*80}\n\n"
        results += f"Base Parameters:\n"
        results += f"Current Asset Price: ${current_price:.2f}\n"
        results += f"Total Asset Value: ${asset_value:,.2f}\n"
        results += f"Total Shares: {total_shares:,.0f}\n"
        results += f"Volatility: {volatility*100:.1f}%\n"
        results += f"Risk-free Rate: {risk_free_rate*100:.1f}%\n"
        results += f"Time to Expiration: {time_to_expiration:.4f} years\n"
        results += f"Delivery Date: {delivery_date.strftime('%Y-%m-%d')}\n\n"
        
        total_portfolio_value = 0
        entity_totals = {}
        
        # Group tranches by entity
        entities = {}
        for tranche in tranches:
            entity = tranche['entity']
            if entity not in entities:
                entities[entity] = []
            entities[entity].append(tranche)
        
        # Calculate results by entity
        for entity_name, entity_tranches in entities.items():
            results += f"\n{'='*60}\n"
            results += f"ENTITY: {entity_name}\n"
            results += f"{'='*60}\n"
            
            entity_total = 0
            
            for tranche in entity_tranches:
                S = current_price
                K = tranche['strike_price']
                T = time_to_expiration
                r = risk_free_rate
                sigma = volatility
                
                if tranche['option_type'] == 'call':
                    option_price = black_scholes_call(S, K, T, r, sigma)
                else:
                    option_price = black_scholes_put(S, K, T, r, sigma)
                
                total_tranche_value = option_price * tranche['num_options']
                entity_total += total_tranche_value
                total_portfolio_value += total_tranche_value
                
                results += f"\n--- TRANCHE {tranche['tranche_num']} ---\n"
                results += f"Option Type: {tranche['option_type'].upper()}\n"
                results += f"Strike Price: ${K:.2f}\n"
                results += f"Number of Options: {tranche['num_options']:,}\n"
                results += f"Price per Option: ${option_price:.4f}\n"
                results += f"Total Tranche Value: ${total_tranche_value:.2f}\n"
                
                # Greeks
                greeks = calculate_greeks(S, K, T, r, sigma)
                results += f"\nGreeks:\n"
                if tranche['option_type'] == 'call':
                    results += f"  Delta: {greeks['delta_call']:.4f}\n"
                    results += f"  Theta: ${greeks['theta_call']:.4f} per day\n"
                    results += f"  Rho: {greeks['rho_call']:.4f}\n"
                else:
                    results += f"  Delta: {greeks['delta_put']:.4f}\n"
                    results += f"  Theta: ${greeks['theta_put']:.4f} per day\n"
                    results += f"  Rho: {greeks['rho_put']:.4f}\n"
                
                results += f"  Gamma: {greeks['gamma']:.4f}\n"
                results += f"  Vega: {greeks['vega']:.4f}\n"
            
            # Entity summary
            entity_totals[entity_name] = entity_total
            results += f"\n{'-'*40}\n"
            results += f"TOTAL FOR {entity_name}: ${entity_total:.2f}\n"
            results += f"As % of Asset: {(entity_total/asset_value)*100:.2f}%\n"
            results += f"{'-'*40}\n"
        
        # Overall portfolio summary
        results += f"\n{'='*50}\n"
        results += f"PORTFOLIO SUMMARY BY ENTITY\n"
        results += f"{'='*50}\n"
        for entity, total in entity_totals.items():
            results += f"{entity}: ${total:.2f} ({(total/asset_value)*100:.2f}%)\n"
        
        results += f"\n{'='*50}\n"
        results += f"TOTAL PORTFOLIO VALUE: ${total_portfolio_value:.2f}\n"
        results += f"Portfolio Value as % of Asset: {(total_portfolio_value/asset_value)*100:.2f}%\n"
        results += f"{'='*50}\n"
        
        self.results_text.insert(tk.END, results)
        
        # Generate charts
        self.create_entity_charts(entities, current_price, volatility, risk_free_rate, time_to_expiration)
        
        # Store results for export
        self.last_results = {
            'base_parameters': {
                'current_price': current_price,
                'total_asset_value': asset_value,
                'total_shares': total_shares,
                'volatility': volatility,
                'risk_free_rate': risk_free_rate,
                'time_to_expiration': time_to_expiration,
                'delivery_date': delivery_date.isoformat()
            },
            'tranches': tranches,
            'entity_totals': entity_totals,
            'total_portfolio_value': total_portfolio_value,
            'portfolio_percentage': (total_portfolio_value/asset_value)*100
        }
        
    
    def create_entity_charts(self, entities, current_price, volatility, risk_free_rate, time_to_expiration):
        # Create a new window for charts
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Entity Option Values - Stacked Bar Chart")
        chart_window.geometry("800x600")
        
        # Create matplotlib figure
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        
        # Prepare data for each entity
        entity_names = list(entities.keys())
        x_pos = np.arange(len(entity_names))
        bar_width = 0.6
        
        # Calculate values for each entity and create stacking data
        all_tranche_values = []  # List of lists, each inner list contains values for one entity
        max_tranches = 0
        
        for entity_name, entity_tranches in entities.items():
            entity_values = []
            
            for tranche in entity_tranches:
                S = current_price
                K = tranche['strike_price']
                T = time_to_expiration
                r = risk_free_rate
                sigma = volatility
                
                if tranche['option_type'] == 'call':
                    option_price = black_scholes_call(S, K, T, r, sigma)
                else:
                    option_price = black_scholes_put(S, K, T, r, sigma)
                
                total_tranche_value = option_price * tranche['num_options']
                entity_values.append({
                    'value': total_tranche_value,
                    'tranche_num': tranche['tranche_num'],
                    'option_type': tranche['option_type'],
                    'strike': tranche['strike_price']
                })
            
            all_tranche_values.append(entity_values)
            max_tranches = max(max_tranches, len(entity_values))
        
        # Generate colors for different tranches
        colors = plt.cm.Set3(np.linspace(0, 1, max_tranches))
        
        # Create stacked bars
        for entity_idx, (entity_name, tranche_values) in enumerate(zip(entity_names, all_tranche_values)):
            bottom = 0
            entity_total = 0
            
            for tranche_idx, tranche_data in enumerate(tranche_values):
                value = tranche_data['value']
                entity_total += value
                
                # Create label for this segment
                label = f"T{tranche_data['tranche_num']} ({tranche_data['option_type'].upper()})\n${tranche_data['strike']:.0f}"
                
                # Create bar segment
                bar = ax.bar(entity_idx, value, bar_width, bottom=bottom, 
                           color=colors[tranche_idx], alpha=0.8, 
                           label=label if entity_idx == 0 else "")
                
                # Add value label on segment if it's large enough
                if value > entity_total * 0.05:  # Only label if segment is >5% of total
                    ax.text(entity_idx, bottom + value/2, f'${value:.0f}', 
                           ha='center', va='center', fontweight='bold', 
                           fontsize=8, color='black')
                
                bottom += value
            
            # Add total value at top of each bar
            ax.text(entity_idx, entity_total + max([sum(tv['value'] for tv in values) 
                   for values in all_tranche_values]) * 0.01, 
                   f'${entity_total:.0f}', ha='center', va='bottom', 
                   fontweight='bold', fontsize=11)
        
        # Customize chart
        ax.set_xlabel('Entities', fontweight='bold', fontsize=12)
        ax.set_ylabel('Option Value ($)', fontweight='bold', fontsize=12)
        ax.set_title('Option Values by Entity\n(Each bar shows stacked individual option values)', 
                    fontweight='bold', fontsize=14)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(entity_names, fontsize=11, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add legend - only show unique tranche labels
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left', 
                     fontsize=9, title="Tranches", title_fontsize=10)
        
        plt.tight_layout()
        
        # Embed matplotlib in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, chart_window)
        toolbar.update()


class TrancheInputWindow:
    def __init__(self, parent, tranche_num, callback, existing_data=None):
        self.callback = callback
        self.window = tk.Toplevel(parent)
        self.window.title(f"Tranche {tranche_num} Input")
        self.window.geometry("300x250")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tranche number
        self.tranche_num = tranche_num
        
        # Entity
        ttk.Label(main_frame, text="Entity:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entity_var = tk.StringVar(value="Entity A")
        ttk.Entry(main_frame, textvariable=self.entity_var, width=15).grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Option type
        ttk.Label(main_frame, text="Option Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.option_type_var = tk.StringVar(value="call")
        option_combo = ttk.Combobox(main_frame, textvariable=self.option_type_var, 
                                   values=["call", "put"], state="readonly", width=15)
        option_combo.grid(row=1, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Strike price
        ttk.Label(main_frame, text="Strike Price ($):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.strike_price_var = tk.StringVar(value="12.00")
        ttk.Entry(main_frame, textvariable=self.strike_price_var, width=15).grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Number of options
        ttk.Label(main_frame, text="Number of Options:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.num_options_var = tk.StringVar(value="1000")
        ttk.Entry(main_frame, textvariable=self.num_options_var, width=15).grid(row=3, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Pre-fill if editing existing data
        if existing_data:
            self.entity_var.set(existing_data[0])
            self.option_type_var.set(existing_data[2])
            self.strike_price_var.set(existing_data[3])
            self.num_options_var.set(existing_data[4])
        
        main_frame.columnconfigure(1, weight=1)
    
    def ok_clicked(self):
        try:
            data = (
                self.entity_var.get(),
                self.tranche_num,
                self.option_type_var.get(),
                self.strike_price_var.get(),
                self.num_options_var.get()
            )
            self.callback(data)
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")


def main():
    root = tk.Tk()
    app = OptionPricingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()