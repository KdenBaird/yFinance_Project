import matplotlib.pyplot as plt
import numpy as np


class GraphNavigator:
    """Manages navigation through multiple graphs with arrow key controls in a single window."""
    
    DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    BAR_COLOR_PRIMARY = '#4682B4'
    BAR_COLOR_SECONDARY = '#FFA07A'
    FIGURE_SIZE = (12, 7)
    
    def __init__(self):
        self.graph_data = []
        self.current_index = 0
        self.fig = None
        self.ax = None
        
    def add_graph(self, fig, title):
        """Extract and store graph data from figure for later display."""
        ax = fig.gca()
        graph_info = self._extract_graph_data(ax, title)
        self.graph_data.append(graph_info)
        plt.close(fig)
        
    def _extract_graph_data(self, ax, title):
        """Extract data and metadata from axes."""
        graph_info = {
            'title': title,
            'type': None,
            'data': None,
            'ylabel': None,
            'bar_label1': None,
            'bar_label2': None
        }
        
        patches = [p for p in ax.patches if hasattr(p, 'get_height')]
        bars = sorted(patches, key=lambda b: b.get_x())
        
        if len(bars) == 5:
            graph_info['type'] = 'single'
            graph_info['data'] = [bar.get_height() for bar in bars]
            graph_info['ylabel'] = ax.get_ylabel()
        elif len(bars) == 10:
            graph_info['type'] = 'comparison'
            data1 = [bars[i].get_height() for i in range(0, len(bars), 2)]
            data2 = [bars[i + 1].get_height() for i in range(0, len(bars), 2)]
            graph_info['data'] = (data1, data2)
            
            legend = ax.get_legend()
            if legend:
                labels = [t.get_text() for t in legend.get_texts()]
                graph_info['bar_label1'] = labels[0] if len(labels) > 0 else 'Data 1'
                graph_info['bar_label2'] = labels[1] if len(labels) > 1 else 'Data 2'
            else:
                graph_info['bar_label1'] = 'Data 1'
                graph_info['bar_label2'] = 'Data 2'
        
        return graph_info
        
    def show_all(self):
        """Display graphs in a single window with navigation."""
        if not self.graph_data:
            return
        
        self.fig, self.ax = plt.subplots(figsize=self.FIGURE_SIZE)
        self.fig.canvas.mpl_connect('key_press_event', self._on_key)
        self._set_window_title('Graph Navigator - Press arrow keys to navigate')
        
        self.current_index = 0
        self._display_current()
        plt.show()
    
    def _display_current(self):
        """Display the current graph in the single window."""
        if not (0 <= self.current_index < len(self.graph_data)):
            return
        
        self.ax.clear()
        graph_info = self.graph_data[self.current_index]
        
        if graph_info['type'] == 'single' and graph_info['data']:
            self._draw_single_bar_chart(graph_info)
        elif graph_info['type'] == 'comparison' and graph_info['data']:
            self._draw_comparison_bar_chart(graph_info)
        
        self._add_navigation_text()
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        self._update_window_title()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def _draw_single_bar_chart(self, graph_info):
        """Draw a single data bar chart."""
        data_axis = graph_info['data']
        bars = self.ax.bar(self.DAYS_OF_WEEK, data_axis, 
                          color=self.BAR_COLOR_PRIMARY, edgecolor='black')
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        self._add_bar_labels(bars, max(data_axis) * 0.02, fontsize=12)
        
        self.ax.set_title(graph_info['title'], fontsize=20, loc='left', pad=20)
        self.ax.set_xlabel('Days of the Week', fontsize=14, labelpad=10)
        self.ax.set_ylabel(graph_info['ylabel'] or 'Value', fontsize=14, labelpad=10)
        
        if data_axis:
            self.ax.set_ylim(0, max(data_axis) * 1.15)
    
    def _draw_comparison_bar_chart(self, graph_info):
        """Draw a comparison bar chart with two datasets."""
        data1, data2 = graph_info['data']
        bar_width = 0.35
        x = np.arange(len(self.DAYS_OF_WEEK))
        
        bars1 = self.ax.bar(x - bar_width/2, data1, bar_width,
                          label=graph_info.get('bar_label1', 'Data 1'),
                          color=self.BAR_COLOR_PRIMARY, edgecolor='black')
        bars2 = self.ax.bar(x + bar_width/2, data2, bar_width,
                          label=graph_info.get('bar_label2', 'Data 2'),
                          color=self.BAR_COLOR_SECONDARY, edgecolor='black')
        
        all_heights = data1 + data2
        offset = max(all_heights) * 0.02 if all_heights else 0
        
        self._add_bar_labels(bars1, offset, fontsize=10)
        self._add_bar_labels(bars2, offset, fontsize=10)
        
        self.ax.set_xlabel('Days of the Week', fontsize=14, labelpad=10)
        self.ax.set_ylabel('Ranges', fontsize=14, labelpad=10)
        self.ax.set_title(graph_info['title'], fontsize=20, loc='left', pad=20)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.DAYS_OF_WEEK)
        self.ax.legend()
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        if all_heights:
            self.ax.set_ylim(0, max(all_heights) * 1.15)
    
    def _add_bar_labels(self, bars, offset, fontsize=12):
        """Add value labels on top of bars."""
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width() / 2, height + offset,
                        f'{height:.2f}', ha='center', va='bottom',
                        fontsize=fontsize, fontweight='bold')
    
    def _add_navigation_text(self):
        """Add navigation instructions to the graph."""
        total = len(self.graph_data)
        nav_text = f'Graph {self.current_index + 1}/{total} | ← Previous | → Next | ESC Close'
        self.ax.text(0.5, -0.15, nav_text, fontsize=10, ha='center',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
                    transform=self.ax.transAxes)
    
    def _set_window_title(self, title):
        """Set window title with backend compatibility."""
        try:
            if hasattr(self.fig.canvas, 'set_window_title'):
                self.fig.canvas.set_window_title(title)
            elif hasattr(self.fig.canvas, 'manager') and hasattr(self.fig.canvas.manager, 'set_window_title'):
                self.fig.canvas.manager.set_window_title(title)
            elif hasattr(self.fig.canvas, 'get_tk_widget'):
                widget = self.fig.canvas.get_tk_widget()
                if hasattr(widget, 'master'):
                    widget.master.title(title)
        except:
            pass
    
    def _update_window_title(self):
        """Update window title with current graph number."""
        total = len(self.graph_data)
        self._set_window_title(f'Graph {self.current_index + 1}/{total}')
    
    def _on_key(self, event):
        """Handle keyboard events for navigation."""
        if event.key in ('right', 'n'):
            self.current_index = (self.current_index + 1) % len(self.graph_data)
            self._display_current()
        elif event.key in ('left', 'p'):
            self.current_index = (self.current_index - 1) % len(self.graph_data)
            self._display_current()
        elif event.key == 'escape':
            plt.close(self.fig)


class Graphs:
    """Creates and manages financial data visualization graphs."""
    
    DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    BAR_COLOR_PRIMARY = '#4682B4'
    BAR_COLOR_SECONDARY = '#FFA07A'
    FIGURE_SIZE = (12, 7)
    
    def __init__(self, ticker_symbol, time, lookback, intraday_start_time=None, intraday_end_time=None, navigator=None):
        self.ticker_symbol = ticker_symbol
        self.time = time
        self.lookback = lookback
        self.intraday_start_time = intraday_start_time
        self.intraday_end_time = intraday_end_time
        self.navigator = navigator
        plt.style.use('ggplot')
    
    def _create_single_bar_chart(self, data_axis, title, ylabel):
        """Create a single data bar chart."""
        fig = plt.figure(figsize=self.FIGURE_SIZE)
        bars = plt.bar(self.DAYS_OF_WEEK, data_axis, 
                      color=self.BAR_COLOR_PRIMARY, edgecolor='black')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height + 0.05,
                    f'{height:.2f}', ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
        
        plt.title(title, fontsize=20, loc='left')
        plt.xlabel('Days of the Week', fontsize=14, labelpad=10)
        plt.ylabel(ylabel, fontsize=14, labelpad=10)
        plt.tight_layout()
        
        if self.navigator:
            self.navigator.add_graph(fig, title)
        else:
            plt.show()
        
        return fig
    
    def _create_comparison_bar_chart(self, data1, data2, title, bar_label1, bar_label2):
        """Create a comparison bar chart with two datasets."""
        bar_width = 0.35
        x = np.arange(len(self.DAYS_OF_WEEK))
        
        fig = plt.figure(figsize=self.FIGURE_SIZE)
        bars1 = plt.bar(x - bar_width/2, data1, bar_width,
                       label=bar_label1, color=self.BAR_COLOR_PRIMARY, edgecolor='black')
        bars2 = plt.bar(x + bar_width/2, data2, bar_width,
                       label=bar_label2, color=self.BAR_COLOR_SECONDARY, edgecolor='black')
        
        for bar in bars1:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:.2f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        for bar in bars2:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:.2f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        plt.xlabel('Days of the Week', fontsize=14, labelpad=10)
        plt.ylabel('Ranges', fontsize=14, labelpad=10)
        plt.title(title, fontsize=20, loc='left')
        plt.xticks(x, self.DAYS_OF_WEEK)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        if self.navigator:
            self.navigator.add_graph(fig, title)
        else:
            plt.show()
        
        return fig
    
    def _prepare_data_series(self, data_by_day):
        """Convert day-indexed data to ordered list."""
        return [data_by_day.get(day, 0) for day in self.DAYS_OF_WEEK]
    
    def display_avg_dr(self, avg_dr_by_day):
        """Display average daily range chart."""
        data_axis = self._prepare_data_series(avg_dr_by_day)
        title = f'Average Daily Range of {self.ticker_symbol} (Past {self.lookback}{self.time})'
        self._create_single_bar_chart(data_axis, title, 'Average Daily Range')
    
    def display_median_dr(self, median_dr_by_day):
        """Display median daily range chart."""
        data_axis = self._prepare_data_series(median_dr_by_day)
        title = f'Median Daily Range of {self.ticker_symbol} (Past {self.lookback}{self.time})'
        self._create_single_bar_chart(data_axis, title, 'Median Daily Range')
    
    def display_avg_idr(self, avg_idr_by_day):
        """Display average intraday range chart."""
        data_axis = self._prepare_data_series(avg_idr_by_day)
        title = (f'Average Intraday Range of {self.ticker_symbol} '
                f'from {self.intraday_start_time}-{self.intraday_end_time}\n'
                f'(Past {self.lookback}{self.time})')
        self._create_single_bar_chart(data_axis, title, 'Average Intraday Range')
    
    def display_median_idr(self, median_idr_by_day):
        """Display median intraday range chart."""
        data_axis = self._prepare_data_series(median_idr_by_day)
        title = (f'Median Intraday Range of {self.ticker_symbol} '
                f'from {self.intraday_start_time} - {self.intraday_end_time} \n'
                f'Past ({self.lookback}{self.time})')
        self._create_single_bar_chart(data_axis, title, 'Median Intraday Range')
    
    def display_avg_dr_and_avg_idr(self, avg_dr_by_day, avg_idr_by_day):
        """Display comparison of average daily vs intraday range."""
        dr_values = self._prepare_data_series(avg_dr_by_day)
        idr_values = self._prepare_data_series(avg_idr_by_day)
        
        if self.intraday_start_time and self.intraday_end_time:
            title = (f'Average Daily Range vs Average Intraday Range '
                    f'({self.intraday_start_time}-{self.intraday_end_time}) of {self.ticker_symbol}')
        else:
            title = f'Average Daily Range vs Average Intraday Range of {self.ticker_symbol}'
        
        self._create_comparison_bar_chart(dr_values, idr_values, title, 'Daily Range', 'Intraday Range')
    
    def display_median_dr_and_median_idr(self, median_dr_by_day, median_idr_by_day):
        """Display comparison of median daily vs intraday range."""
        dr_values = self._prepare_data_series(median_dr_by_day)
        idr_values = self._prepare_data_series(median_idr_by_day)
        
        if self.intraday_start_time and self.intraday_end_time:
            title = (f'Median Daily Range vs Median Intraday Range '
                    f'({self.intraday_start_time}-{self.intraday_end_time}) of {self.ticker_symbol}')
        else:
            title = f'Median Daily Range vs Median Intraday Range of {self.ticker_symbol}'
        
        self._create_comparison_bar_chart(dr_values, idr_values, title,
                                         'Median Daily Range', 'Median Intraday Range')
    
    def display_avg_dr_and_median_dr(self, avg_dr_by_day, median_dr_by_day):
        """Display comparison of average vs median daily range."""
        avg_dr_values = self._prepare_data_series(avg_dr_by_day)
        median_dr_values = self._prepare_data_series(median_dr_by_day)
        title = f'Average Daily Range vs Median Daily Range of {self.ticker_symbol}'
        self._create_comparison_bar_chart(avg_dr_values, median_dr_values, title,
                                         'Average Daily Range', 'Median Daily Range')
    
    def display_avg_idr_and_median_idr(self, avg_idr_by_day, median_idr_by_day):
        """Display comparison of average vs median intraday range."""
        avg_idr_values = self._prepare_data_series(avg_idr_by_day)
        median_idr_values = self._prepare_data_series(median_idr_by_day)
        title = (f'Average Intraday Range vs Median Intraday Range of \n'
                f'{self.ticker_symbol} from {self.intraday_start_time} - {self.intraday_end_time} '
                f'Past ({self.lookback}{self.time})')
        self._create_comparison_bar_chart(avg_idr_values, median_idr_values, title,
                                         'Average Intraday Range', 'Median Intraday Range')
