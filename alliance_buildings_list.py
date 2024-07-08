from selenium.webdriver.common.by import By
from driver import launch_driver
import json


def course_dict_sorting(
    course_dict: dict[str, list[str]], building_name: str, day: str
):
    if day[0:3] in building_name:
        for course in course_dict.keys():
            if course in building_name:
                course_dict[course].append(building_name)
                break


def create_course_dict(service: str):
    if service == "ems":
        course_dict = {
            "Ambulance Officer": [],
            "Critical Care": [],
            "HART": [],
            "SORT": [],
            "Tactical Command": [],
        }
    elif service == "police":
        course_dict = {
            "Dog Handling": [],
            "Drone Operator": [],
            "Firearms": [],
            "Level 1 Public Order": [],
            "Level 2 Public Order": [],
            "Mounted Police": [],
            "Police Aviation": [],
            "Police Inspector": [],
            "Police Medic": [],
            "Police Search Advisor": [],
            "Police Sergeant": [],
            "Roads Policing": [],
        }
    elif service == "fire":
        course_dict = {
            "ARF": [],
            "Co-Responder": [],
            "Fire Drone Operator": [],
            "Fire Lifeguard": [],
            "Hazmat": [],
            "HVPT": [],
            "Mobile Command": [],
        }
    elif service == "lifeboat":
        course_dict = {
            "Coastal Air Rescue": [],
            "Coastal Command": [],
            "Coastal Search Advis": [],
            "Drone Operator": [],
            "Flood First Responder": [],
            "Hovercraft Command": [],
            "Jet Ski Handling": [],
            "Lifeboat Operations": [],
            "Lifeguard Training": [],
            "Mud Rescue": [],
            "Rope Rescue": [],
            "SAR Search Management": [],
        }

    return course_dict


driver = launch_driver()
driver.get("https://missionchief.co.uk/verband/gebauede")

# Search attribute: EMS = AD, Police = AE, Fire = AF, Lifeboat = AI
buildings = driver.find_elements(By.CSS_SELECTOR, "[search_attribute^='AD']")

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daily_courses = {}
for day in days:
    # Options: ems, police, fire, lifeboat
    course_dict = create_course_dict("ems")
    for building in buildings:
        building_name = building.find_element(
            By.CSS_SELECTOR, "td:nth-child(2) > a"
        ).text

        course_dict_sorting(course_dict, building_name, day)
    daily_courses[day] = course_dict

# Store the dict into a json file
with open("json/ems-daily-all-buildings.json", "w") as json_file:
    json.dump(daily_courses, json_file, indent=4)

driver.quit()
