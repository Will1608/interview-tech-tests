"""
    Coding test: Bookings report for a transportation operator

    Our revenue management solution CAYZN extracts from an inventory system the transport plan of an operator (trains,
    flights or buses with their itineraries, stops and timetable) and allows our users to analyze sales, forecast the
    demand and optimize their pricing.

    In this project you will manipulate related concepts to build a simple report. We will assess your ability to read
    existing code and to understand the data model in order to develop new features. Two items are essential: the final
    result, and the quality of your code.

    Questions and example data are at the bottom of the script. Do not hesitate to modify existing code if needed.

    Good luck!
"""

import datetime
from typing import List


class Service:
    """A service is a facility transporting passengers between two or more stops at a specific departure date.

    A service is uniquely defined by its name and a departure date. It is composed of one or more legs (which
    represent its stops and its timetable), which lead to multiple Origin-Destination (OD) pairs, one for each possible
    trip that a passenger can buy.
    """

    def __init__(self, name: str, departure_date: datetime.date):
        self.name = name
        self.departure_date = departure_date
        self.legs: List[Leg] = []
        self.ods: List[OD] = []

    @property
    def day_x(self):
        """Number of days before departure.

        In revenue management systems, the day-x scale is often preferred because it is more convenient to manipulate
        compared to dates.
        """
        return (datetime.date.today() - self.departure_date).days

    @property
    def itinerary(self):
        """Ordered list of stops."""

        return [leg.origin for leg in self.legs] + [self.legs[-1].destination]

    def load_itinerary(self, itinerary: List["Station"]) -> None:
        """sets legs and ODs for given service"""

        station_in_itinerary_count = len(itinerary)

        for origin_idx in range(station_in_itinerary_count - 1):

            self.legs.append(Leg(self, itinerary[origin_idx], itinerary[origin_idx + 1]))

            for destination_idx in range( origin_idx + 1, station_in_itinerary_count):
                
                self.ods.append(OD(self, itinerary[origin_idx], itinerary[destination_idx]))

    def load_passenger_manifest(self, passengers: List["Passenger"]) -> None:
        for passenger in passengers:
            print(OD(self, passenger.origin, passenger.destination))
            print(self.ods[0])

class Station:
    """A station is where a service can stop to let passengers board or disembark."""

    def __init__(self, name: str):
        self.name = name


class Leg:
    """A leg is a set of two consecutive stops.

    Example: a service whose itinerary is A-B-C-D has three legs: A-B, B-C and C-D.
    """

    def __init__(self, service: Service, origin: Station, destination: Station):
        self.service = service
        self.origin = origin
        self.destination = destination


class OD:
    """An Origin-Destination (OD) represents the transportation facility between two stops, bought by a passenger.

    Example: a service whose itinerary is A-B-C-D has up to six ODs: A-B, A-C, A-D, B-C, B-D and C-D.
    """

    def __init__(self, service: Service, origin: Station, destination: Station):
        self.service = service
        self.origin = origin
        self.destination = destination
        self.passengers: List[Passenger] = []

    @property
    def legs(self):
        """Legs in OD."""
        itinerary: Service.itinerary = service.itinerary

        return [self.service.legs[i] for i in range(itinerary.index(self.origin), itinerary.index(self.destination))]


class Passenger:
    """A passenger that has a booking on a seat for a particular origin-destination."""

    def __init__(self, origin: Station, destination: Station, sale_day_x: int, price: float):
        self.origin = origin
        self.destination = destination
        self.sale_day_x = sale_day_x
        self.price = price


# Let's create a service to represent a train going from Paris to Marseille with Lyon as intermediate stop. This service
# has two legs and sells three ODs.

ply = Station("ply")  # Paris Gare de Lyon
lpd = Station("lpd")  # Lyon Part-Dieu
msc = Station("msc")  # Marseille Saint-Charles
service = Service("7601", datetime.date.today() + datetime.timedelta(days=7))
leg_ply_lpd = Leg(service, ply, lpd)
leg_lpd_msc = Leg(service, lpd, msc)
service.legs = [leg_ply_lpd, leg_lpd_msc]
od_ply_lpd = OD(service, ply, lpd)
od_ply_msc = OD(service, ply, msc)
od_lpd_msc = OD(service, lpd, msc)
service.ods = [od_ply_lpd, od_ply_msc, od_lpd_msc]

# 1. Add a property named `itinerary` in `Service` class, that returns the ordered list of stations where the service
# stops. Assume legs in a service are properly defined, without inconsistencies.

assert service.itinerary == [ply, lpd, msc]

# 2. Add a property named `legs` in `OD` class, that returns legs that are crossed by this OD. You can use the
# `itinerary` property to find the index of the matching legs.

assert od_ply_lpd.legs == [leg_ply_lpd]
assert od_ply_msc.legs == [leg_ply_lpd, leg_lpd_msc]
assert od_lpd_msc.legs == [leg_lpd_msc]

# 3. Creating every leg and OD for a service is not convenient, to simplify this step, add a method in `Service` class
# to create legs and ODs associated to list of stations. The signature of this method should be:
# load_itinerary(self, itinerary: List["Station"]) -> None:

itinerary = [ply, lpd, msc]
service = Service("7601", datetime.date.today() + datetime.timedelta(days=7))
service.load_itinerary(itinerary)
assert len(service.legs) == 2
assert service.legs[0].origin == ply
assert service.legs[0].destination == lpd
assert service.legs[1].origin == lpd
assert service.legs[1].destination == msc
assert len(service.ods) == 3
od_ply_lpd = next(od for od in service.ods if od.origin == ply and od.destination == lpd)
od_ply_msc = next(od for od in service.ods if od.origin == ply and od.destination == msc)
od_lpd_msc = next(od for od in service.ods if od.origin == lpd and od.destination == msc)

# 4. Create a method in `Service` class that reads a passenger manifest (a list of all bookings made for this service)
# and that allocates bookings across ODs. When called, it should fill the `passengers` attribute of each OD instances
# belonging to the service. The signature of this method should be:
# load_passenger_manifest(self, passengers: List["Passenger"]) -> None:

service.load_passenger_manifest(
    [
        Passenger(ply, lpd, -30, 20),
        Passenger(ply, lpd, -25, 30),
        Passenger(ply, lpd, -20, 40),
        Passenger(ply, lpd, -20, 40),
        Passenger(ply, msc, -10, 50),
    ]
)
od_ply_lpd, od_ply_msc, od_lpd_msc = service.ods
assert len(od_ply_lpd.passengers) == 4
assert len(od_ply_msc.passengers) == 1
assert len(od_lpd_msc.passengers) == 0

# 5. Write a property named `passengers` in `Leg` class that returns passengers occupying a seat on this leg.

# assert len(service.legs[0].passengers) == 5
# assert len(service.legs[1].passengers) == 1

# 6. We want to generate a report about sales made each day, write a `history()` method in `OD` class that returns a
# list of data point, each data point is a three elements array: [day_x, cumulative number of bookings, cumulative
# revenue].

# history = od_ply_lpd.history()
# assert len(history) == 3
# assert history[0] == [-30, 1, 20]
# assert history[1] == [-25, 2, 50]
# assert history[2] == [-20, 4, 130]

# 7. In the final solution, we have a demand matrix estimated using machine learning that gives us the estimated demand for any day_x and price 
# The goal of this question is to write an algorithm that find the optimal path to maximize the revenue through this matrix
# Given a MxN matrix of integers superior to 0, where (0,0) is the top left corner and (m-1,n-1) is the bottom right corner, 
# we want to write a program that gives the path that maximizes the sum of integers along it. 
# Only permitted move are to the right or bottom. Each position can only be visited once.
# The function that solves the problem should looks something like this
# matrix = 1 1 8 
#          3 2 1
# assert max_path_finder([[1, 1, 8], [3, 2, 1]]) == 11, [(0,0) (0,1) (0,2) (1,2)]
# 
# You code should pass all the following asserts
# assert max_path_finder([[1, 2, 3], [3, 4, 5]]) == (13, [(0, 0), (1, 0), (1, 1), (1, 2)])
# assert max_path_finder([[1, 2, 25], [3, 4, 5]]) == (33, [(0, 0), (0, 1), (0, 2), (1, 2)])
# assert max_path_finder([[1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]]) == (5, [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (4, 1), (4, 2)])
# assert max_path_finder([[1, 0, 5], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]]) == (6, [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2)])
# assert max_path_finder([[1, 0, 5], [1, 0, 0], [1, 10, 1], [1, 0, 1], [1, 0, 0]]) == (15, [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2)])