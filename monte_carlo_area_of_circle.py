"""
Program to Compute the Area of a Circle using Monte Carlo Simulation
The number 4 in the area_estimate equation arises from the relationship between the area of the circle and the area of the square that we use in the Monte Carlo simulation.
Let me break it down:
Square Area: The square that encompasses the circle has a side length of 2 times the radius (to fully contain the circle). Therefore, the area of the square is calculated as (2 * radius)**2, which simplifies to 4 * radius**2.
Ratio of Areas: The Monte Carlo method essentially compares the number of points that fall inside the circle to the total number of points generated within the square. This ratio approximates the ratio of the circle's area to the square's area.
Estimated Circle Area: To obtain the estimated area of the circle, we take the ratio of points inside the circle to the total points and multiply it by the area of the square. This is where the 4 comes into play:
area_estimate = (in_circle / num_points) * (4 * radius**2)
Use code with caution.
In essence, we are scaling the ratio of points by the area of the square to get an estimate of the circle's area. The 4 is a factor that accounts for the difference in area between the circle and the square we use for the simulation.
"""

import random
def monte_carlo_circle_area(radius, num_points):
    """
    The function `monte_carlo_circle_area` estimates the area of a circle using the Monte Carlo method
    by generating random points within a square and determining the ratio of points inside the circle to
    the total points.

    :param radius: The radius parameter in the `monte_carlo_circle_area` function represents the radius
    of the circle for which we want to estimate the area using the Monte Carlo method. This radius
    determines the size of the circle within which random points are generated to estimate the area
    :param num_points: The `num_points` parameter in the `monte_carlo_circle_area` function represents
    the number of random points that will be generated within a square with side length `2 * radius`.
    These points will be used to estimate the area of a circle with the given radius using the Monte
    Carlo method
    :return: an estimate of the area of a circle with the given radius using the Monte Carlo method.
    """
    in_circle = 0
    for _ in range(num_points):
        x = random.uniform(-radius, radius)
        y = random.uniform(-radius, radius)
        if x**2 + y**2 <= radius**2:
            in_circle += 1

    area_estimate = (in_circle / num_points) * (
        4 * radius**2
    )  # Area of Square = 4 * radius**2
    return area_estimate


if __name__ == "__main__":
    radius = float(input("Enter the radius of the circle: "))
    num_points = int(input("Enter the number of random points: "))

    estimated_area = monte_carlo_circle_area(radius, num_points)
    print("Estimated area of the circle:", estimated_area)
