class DynamicTPSL:
    def __init__(self, df, tp_base, sl_base):
        """
        :param df: The DataFrame with your stock data
        :param tp_base: Base value for take profit
        :param sl_base: Base value for stop loss
        """
        self.df = df
        self.tp_base = tp_base
        self.sl_base = sl_base
    
    def get_day_of_week_multiplier(self, date):
        day_of_week = date.weekday()  # Monday = 0, Sunday = 6
        # Define multipliers based on the day of the week (example values)
        multipliers = {
            0: 1.1,  # Monday
            1: 1.2,  # Tuesday
            2: 1.0,  # Wednesday
            3: 0.9,  # Thursday
            4: 0.8   # Friday
        }
        return multipliers.get(day_of_week, 1)  # Default to 1 if the day is missing

    def calculate_tp_sl(self, date, current_price, position_type):
        """
        Calculate dynamic TP/SL based on day of the week and position type.
        :param date: Date of the trade (used to get the day of the week)
        :param current_price: Current price of the asset
        :param position_type: 'long' or 'short'
        """
        multiplier = self.get_day_of_week_multiplier(date)
        
        if position_type == 'long':
            tp = current_price + (self.tp_base * multiplier)
            sl = current_price - (self.sl_base * multiplier)
        elif position_type == 'short':
            tp = current_price - (self.tp_base * multiplier)
            sl = current_price + (self.sl_base * multiplier)
        
        return tp, sl
