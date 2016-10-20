class SimpleStats:
    def __init__(self):
        self.number_list = []

    def add_value(self, value):
        self.number_list.append(value)

    def get_min(self):
        return min(self.number_list)

    def get_max(self):
        return max(self.number_list)

    def get_sum(self):
        return sum(self.number_list)

    def get_average(self):
        if len(self.number_list) == 0:
            return 0

        return sum(self.number_list) / len(self.number_list)

    
stats = SimpleStats()

new_number = input('Enter a number for the list: ')

while new_number != '':
    stats.add_value(eval(new_number))
    new_number = input('Enter a number for the list: ')

print('The smallest number is', stats.get_min())
print('The largest number is', stats.get_max())
print('The sum of the list is', stats.get_sum())
print('The average of the list is', stats.get_average())
