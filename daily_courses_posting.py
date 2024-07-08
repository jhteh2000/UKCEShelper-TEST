from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from driver import launch_driver
import json
import asyncio
import discord


ALL_EDUCATION_KEYS = {
    "EMS": {
        "Ambulance Officer": "ems_mobile_command",
        "Critical Care": "critical_care",
        "HART": "hazard_response_ems",
        "SORT": "special_operation_response",
        "Tactical Command": "elw2_ems",
    },
    "Police": {
        "Dog Handling": "k9",
        "Drone Operator": "drone",
        "Firearms": "swat",
        "Level 1 Public Order": "level_1_public_order",
        "Level 2 Public Order": "level_2_public_order",
        "Mounted Police": "police_horse",
        "Police Aviation": "polizeihubschrauber",
        "Police Inspector": "police_inspector",
        "Police Medic": "police_medic",
        "Police Search Advisor": "search_and_rescue",
        "Police Sergeant": "police_sergeant",
        "Roads Policing": "traffic_police",
    },
    "Fire": {
        "ARF": "arff",
        "Co-Responder": "coresponder",
        "Fire Drone Operator": "drone",
        "Fire Lifeguard": "gw_wasserrettung",
        "Hazmat": "gw_gefahrgut",
        "HVPT": "pump",
        "Mobile Command": "elw2",
    },
    "Lifeboat": {
        "Coastal Air Rescue": "coastal_rescue_pilot",
        "Coastal Command": "coastal_command",
        "Coastal Search Advis": "search_and_rescue",
        "Drone Operator": "drone",
        "Flood First Responder": "flood_equipment",
        "Hovercraft Command": "hover_boat_elw",
        "Jet Ski Handling": "jetski",
        "Lifeboat Operations": "ocean_navigation",
        "Lifeguard Training": "gw_wasserrettung",
        "Mud Rescue": "coastal_mud_rescue",
        "Rope Rescue": "gw_hoehenrettung",
        "SAR Search Management": "search_and_rescue_command",
    },
}


async def start_course(driver: Chrome, service: str, building_name: str, course: str):
    education_keys = ALL_EDUCATION_KEYS[service]
    error_message = None

    # Check if alliance buildings page is loaded
    while True:
        try:
            # Find the alliance buildings table
            # Will raise exception if page is not loaded
            driver.find_element(By.CSS_SELECTOR, "#alliance_buildings_table")
        except:
            # If page not loaded, wait for 5 seconds then reload the page
            await asyncio.sleep(5)
            driver.get("https://missionchief.co.uk/verband/gebauede")
            await asyncio.sleep(1)
        else:
            # Exit while loop if page loaded successfully
            break

    try:
        # Navigate to the building
        search_attribute = f"[search_attribute='{building_name}']"
        try:
            building = driver.find_element(By.CSS_SELECTOR, search_attribute)
        except:
            raise Exception("Building not found")

        await asyncio.sleep(0.5)

        # "Start a new training course" button
        try:
            start_course = building.find_element(By.CSS_SELECTOR, "td:nth-child(3) > a")
            start_course.click()
        except:
            raise Exception("All classrooms are being used")

        await asyncio.sleep(0.5)

        # Select number of rooms to use
        try:
            rooms = Select(driver.find_element(By.CSS_SELECTOR, "#building_rooms_use"))
            rooms.select_by_visible_text("4")
        except:
            raise Exception("There are fewer than 4 available rooms")

        await asyncio.sleep(0.5)

        # Select course type
        education_key = f"[education_key='{education_keys[course]}']"
        try:
            course_option = driver.find_element(By.CSS_SELECTOR, education_key)
            course_option.click()
        except:
            raise Exception("Course not found")

        await asyncio.sleep(0.5)

        # Select post duration
        try:
            duration = Select(
                driver.find_element(By.CSS_SELECTOR, "#alliance_duration")
            )
            duration.select_by_visible_text("1 day")
        except:
            raise Exception("The '1-day duration' option is not available")

        await asyncio.sleep(0.5)

        # Start course
        try:
            educate = driver.find_element(
                By.CSS_SELECTOR,
                "#schooling > form > nav > div > div:nth-child(1) > input",
            )
            educate.click()
        except:
            raise Exception("The 'Educate' button is not available")

        # print(course, "posted on", building_name)
        status = True
    except Exception as e:
        # print("Error starting course on", building_name)
        status = False
        error_message = e

    await asyncio.sleep(1)
    if driver.current_url != "https://missionchief.co.uk/verband/gebauede":
        driver.get("https://missionchief.co.uk/verband/gebauede")
        await asyncio.sleep(1)
    return status, error_message


async def post_daily_course(
    interaction: discord.Interaction, day_to_post: str, service: str
):
    status_overall = True

    with open(f"json/{service.lower()}-daily-all-buildings.json") as json_file:
        buildings = json.load(json_file)

    buildings_to_post = buildings[day_to_post]

    driver = await launch_driver()
    driver.get("https://missionchief.co.uk/verband/gebauede")
    await asyncio.sleep(1)

    daily_courses = list(ALL_EDUCATION_KEYS[service].keys())
    for course in daily_courses:
        for bname in buildings_to_post[course]:
            status, error_message = await start_course(driver, service, bname, course)
            if status:
                await interaction.channel.send(
                    content=f":white_check_mark: {course} posted on {bname}\n"
                )
            else:
                await interaction.channel.send(
                    content=f":warning: Error posting {course} on {bname}: {error_message}\n"
                )
                status_overall = False

    emoji = {
        "EMS": ":ambulance:",
        "Police": ":police_car:",
        "Fire": ":fire_engine:",
        "Lifeboat": ":motorboat:",
    }
    if status_overall:
        await interaction.channel.send(
            content=f"{emoji[service]} :white_check_mark: Daily {service} courses have been posted successfully :white_check_mark:"
        )
    else:
        await interaction.channel.send(
            content=f"{emoji[service]} :warning: There are some errors in posting the daily {service} courses :warning:"
        )

    driver.quit()
