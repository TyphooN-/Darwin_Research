from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Path to your ChromeDriver
chrome_driver_path = '/usr/bin/chromedriver'

# Setup WebDriver with the ChromeDriver path
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Open the Darwinex Zero Capital Allocation calculator page
driver.get('https://www.darwinexzero.com/capital-allocation')

# Define input variables
current_month_return_value = '50'
prior_5_months_return_value = '50'

# Prepare to store results
results = []

try:
    for drawdown_value in range(-1, -1001, -1):  # -0.1% to -100% in increments of 0.1%
        # Locate the input fields by their 'name' attribute and clear them twice to ensure they are empty
        current_month_return = driver.find_element(By.NAME, 'currentMonthReturn')
        current_month_return.clear()
        current_month_return.send_keys('')  # Extra clear step
        current_month_return.clear()
        current_month_return.send_keys(current_month_return_value)

        prior_5_months_return = driver.find_element(By.NAME, 'prior5MonthsReturn')
        prior_5_months_return.clear()
        prior_5_months_return.send_keys('')  # Extra clear step
        prior_5_months_return.clear()
        prior_5_months_return.send_keys(prior_5_months_return_value)

        max_drawdown_6m = driver.find_element(By.NAME, 'maxDrawdown6M')
        max_drawdown_6m.clear()
        max_drawdown_6m.send_keys('')  # Extra clear step
        max_drawdown_6m.clear()
        max_drawdown_6m.send_keys(str(drawdown_value / 10))  # Convert to percentage

        # Click the "Calculate" button
        calculate_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        calculate_button.click()

        # Increase wait time to 20 seconds
        wait = WebDriverWait(driver, 20)

        # Debugging: Print the page source after calculation to verify if values are displayed
        time.sleep(2)  # Wait to allow time for the results to load
#        print(driver.page_source)

        # Locate the rating and allocation elements
        rating_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//p[text()="Your rating:"]/following-sibling::p/span')))
        allocation_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//p[text()="Your expected allocation this month:"]/following-sibling::p/span')))

        # Extract the result text
        rating = rating_element.text
        allocation = allocation_element.text

        # Debugging: Print values to verify they are captured correctly
        result = {
            'Current Month Return': current_month_return_value,
            'Prior 5 Months Return': prior_5_months_return_value,
            'Max Drawdown 6M': drawdown_value / 10,
            'Rating': rating,
            'Expected Allocation This Month': allocation
        }

        # Print all values to verify
        print(result)

        # Store results along with input variables
        results.append({
            'Current Month Return': current_month_return_value,
            'Prior 5 Months Return': prior_5_months_return_value,
            'Max Drawdown 6M': drawdown_value / 10,
            'Rating': rating,
            'Expected Allocation This Month': allocation
        })

        time.sleep(1)  # Add a small delay to avoid overwhelming the server

finally:
    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv('Darwinex_Calculation_Results.csv', index=False)

    # Close the browser
    driver.quit()
