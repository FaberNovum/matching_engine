import sortedcontainers

from threading import Thread
from collections import deque

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

        # Cumulative ask volume
        askvalues = [0]
        for i in range(len(self.asks)):
            askvalues.append(sum([self.asks[x].quantity for x in range(i + 1)]))
        askvalues.append(sum([ask.quantity for ask in self.asks]))
        askvalues.sort(reverse=True)

        # Draw big side
        x = [self.bids[0].price] + [order.price for order in self.bids] + [self.bids[-1].price]
        ax.step(x, bidvalues, color='green')

        # Draw ask side
        x = [self.asks[-1].price] + sorted([order.price for order in self.asks], reverse=True) + [self.asks[0].price]
        ax.step(x, askvalues, color='red')

        ax.set_xlim([min(order.price for order in self.bids), max(order.price for order in self.asks)])
        plt.show()
        if save:
            fig.savefig('plot.png', transparent=True)

class MatchingEngine:
    def __init__(self, threaded=False):
        self.queue = deque()
        self.orderbook = Orderbook()
        self.trades = deque()
        self.threaded = threaded
        if self.threaded:
            self.thread = Thread(target=self.run)
            self.thread.start()

    def process(self, order):
        if self.threaded:
            self.queue.append(order)
        else:
            self.match(order)

    def get_trades(self):
        trades = list(self.trades)
        return trades

    def match(self, order):
        if order.side == 'buy' and order.price >= self.orderbook.best_ask():
            # Buy order crossed the spread
            filled = 0
            consumed_asks =[]
            for i in range(len(self.orderbook.asks)):
                ask = self.orderbook.asks[i]

                if ask.price > order.price:
                    break # Price of ask is too high, stop filling the order
                elif filled == order.quantity:
                    break # Order filled

                if filled + ask.quantity <= order.quantity: # order not yet filled, ask will consumed as whole
                    filled += ask.quantity
                    trade = Trade(ask.price, ask.quantity)
                    self.trades.append(trade)
                    consumed_asks.append(ask)
                elif filled + ask.quantity > order.quantity: # order is filled, ask willl be consumed partially
                    volume = order.quantity-filled
                    filled += volume
                    trade = Trade(ask.price, volume)
                    self.trades.append(trade)
                    ask.quantity -= volume
            # Place any remaining volume in Limit Order Book
            if filled < order.quantity:
                self.orderbook.add(Order("limit", "buy", order.price, order.quantity-filled))
                
            # Remove asks used for filling order
            for ask in consumed_asks:
                self.orderbook.remove(ask)
        elif order.side == 'sell' and order.price <= self.orderbook.best_bid():
            # Sell order crossed the spread
            filled = 0
            consumed_bids = []
