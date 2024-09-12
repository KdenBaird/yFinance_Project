import matplotlib.pyplot as plt
import numpy as np

class Graphs:
    def __init__(self, ticker_symbol, time, lookback, intraday_start_time=None, intraday_end_time=None):
        self.ticker_symbol = ticker_symbol
        self.time = time
        self.lookback = lookback
        self.intraday_start_time = intraday_start_time
        self.intraday_end_time = intraday_end_time
        self.days_axis = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        plt.style.use('ggplot')
    
    def create_single_data_bar_chart(self, data_axis, title, ylabel):
        plt.figure(figsize=(12, 7))
        bars = plt.bar(self.days_axis, data_axis, color='#4682B4', edgecolor='black')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Add text on top of the bars with good style
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height + 0.05,
                     f'{height:.2f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        plt.title(title, fontsize=20, loc='left')
        plt.xlabel('Days of the Week', fontsize=14, labelpad=10)
        plt.ylabel(ylabel, fontsize=14, labelpad=10)
        
        plt.tight_layout()
        plt.show()

    def create_comparison_data_bar_chart(self, data1, data2, title, bar_label1, bar_label2):
        bar_width = 0.35  
        x = np.arange(len(self.days_axis))  # Label locations

        plt.figure(figsize=(12, 7))

        # Plot the bars
        bars1 = plt.bar(x - bar_width/2, data1, bar_width, label=bar_label1, color='#4682B4', edgecolor='black')
        bars2 = plt.bar(x + bar_width/2, data2, bar_width, label=bar_label2, color='#FFA07A', edgecolor='black')

        # Add text on top of the bars
        for bar in bars1:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
        for bar in bars2:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Add labels, title, and legend
        plt.xlabel('Days of the Week', fontsize=14, labelpad=10)
        plt.ylabel('Ranges', fontsize=14, labelpad=10)
        plt.title(title, fontsize=20, loc='left')
        plt.xticks(x, self.days_axis)
        plt.legend()

        # Display grid
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        # Show the plot
        plt.show()

    def display_avg_dr(self, avg_dr_by_day):
        # Note the get method is exclusive to dictionaries, first parameter is key, second parameter is what the value is set if none is given
        data_axis = [avg_dr_by_day.get(day, 0) for day in self.days_axis]
        title = f'Average Daily Range of {self.ticker_symbol} (Past {self.lookback}{self.time})'
        ylabel = 'Average Daily Range'
        self.create_single_data_bar_chart(data_axis, title, ylabel)

    def display_median_dr(self, median_dr_by_day):
        data_axis = [median_dr_by_day.get(day, 0) for day in self.days_axis]
        title = f'Median Daily Range of {self.ticker_symbol} (Past {self.lookback}{self.time})'
        ylabel = 'Median Daily Range'
        self.create_single_data_bar_chart(data_axis, title, ylabel)

    def display_avg_idr(self, avg_idr_by_day):
        data_axis = [avg_idr_by_day.get(day, 0) for day in self.days_axis]
        title = f'Average Intraday Range of {self.ticker_symbol} from {self.intraday_start_time}-{self.intraday_end_time}\n(Past {self.lookback}{self.time})'
        ylabel = 'Average Intraday Range'
        self.create_single_data_bar_chart(data_axis, title, ylabel)
        
    def display_median_idr(self, median_idr_by_day):
        data_axis = [median_idr_by_day.get(day, 0) for day in self.days_axis]
        title = f'Median Intraday Range of {self.ticker_symbol} from {self.intraday_start_time} - {self.intraday_end_time} \n Past ({self.lookback}{self.time})'
        ylabel = 'Median Intraday Range'
        self.create_single_data_bar_chart(data_axis, title, ylabel)
    
    def display_avg_dr_and_avg_idr(self, avg_dr_by_day, avg_idr_by_day):
        dr_values = [avg_dr_by_day.get(day, 0) for day in self.days_axis]
        idr_values = [avg_idr_by_day.get(day, 0) for day in self.days_axis] 
        title = f'Average Daily Range vs Average Intraday Range of {self.ticker_symbol}'
        bar_label1 = 'Daily Range'
        bar_label2 = 'Intraday Range'

        self.create_comparison_data_bar_chart(dr_values, idr_values, title, bar_label1, bar_label2)

    def display_median_dr_and_median_idr(self, median_dr_by_day, median_idr_by_day):
        dr_values = [median_dr_by_day.get(day, 0) for day in self.days_axis]
        idr_values = [median_idr_by_day.get(day, 0) for day in self.days_axis]
        title = f'Median Daily Range vs Median Intraday Range of {self.ticker_symbol}'
        bar_label1 = 'Median Daily Range'
        bar_label2 = 'Median Intraday Range'
        
        self.create_comparison_data_bar_chart(dr_values, idr_values, title, bar_label1, bar_label2)

    def display_avg_dr_and_median_dr(self, avg_dr_by_day, median_dr_by_day):
        avg_dr_values = [avg_dr_by_day.get(day, 0) for day in self.days_axis]
        median_dr_values = [median_dr_by_day.get(day, 0) for day in self.days_axis]
        title = f'Average Daily Range vs Median Daily Range of {self.ticker_symbol}'
        bar_label1 = 'Average Daily Range'
        bar_label2 =  'Median Daily Range'
        
        self.create_comparison_data_bar_chart(avg_dr_values, median_dr_values, title, bar_label1, bar_label2)

    def display_avg_idr_and_median_idr(self, avg_idr_by_day, median_idr_by_day):
        avg_idr_values = [avg_idr_by_day.get(day, 0) for day in self.days_axis]
        median_idr_values = [median_idr_by_day.get(day, 0) for day in self.days_axis]
        title = f'Average Intraday Range vs Median Intrday Range of \n {self.ticker_symbol} from {self.intraday_start_time} - {self.intraday_end_time} Past ({self.lookback}{self.time})'
        bar_label1 = 'Average Intraday Range'
        bar_label2 = 'Meidan Intraday Range'
        
        self.create_comparison_data_bar_chart(avg_idr_values, median_idr_values, title, bar_label1, bar_label2)