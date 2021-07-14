import sortedcontainers

class Order:
    def __init__(self, order_type, side, price, quantity):
        self.type = order_type
        self.side = side.lower()
        self.price = price
        self.quantity = quantity

class Trade:
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity

class OrderBook:

    def __init__(self, bids=[], asks=[]):
        self.bids = sortedcontainers.SortedList(bids, key = lambda order: -order.price)
        self.asks = sortedcontainers.SortedList(asks, key = lambda order: order.price)
    
    def __len__(self):
        return len(self.bids) + len(self.asks)

    def add(self, order):
        if order.directoin == 'buy':
            self.bids.insert(self.bids.bisect_right(order), order)
        elif order.direction == 'sell':
            self.asks.insert(self.asks.bisect_right(order), order)

    def remove(self, order):
        if order.direction == 'buy':
            self.bids.remove(order)
        elif order.direction == 'sell':
            self.asks.remove(order)
    
    def plot(self):
        fig = plt.figure(figsize=(10,5))
        ax = fig.add_subplot(111)
        ax.set_title("Limit Order Book")
    
        ax.set_xlabel('Price')
        ax.set_ylabel('Quantity')

        # Cumulative bid volume
        bidvalues = [0]
        for i in range(len(self.bids)):
            bidvalues.append(sum([self.bids[x].quantity for x in range(i+1)]))
        bidvalues.append(sum([bid.quantity for bid in self.vids]))
        bidvalues.sort()