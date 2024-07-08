from selenium.webdriver.common.by import By
from driver import launch_driver
import asyncio
import discord


async def clear_transport(interaction: discord.Interaction, mission_url: str):
    driver = launch_driver()
    driver.get(mission_url)
    await asyncio.sleep(1)
    cleared_count = 0

    while True:
        try:
            on_scene_table_body = driver.find_element(
                By.CSS_SELECTOR, "#mission_vehicle_at_mission > tbody"
            )

            on_scene_table_first_row = on_scene_table_body.find_element(
                By.CSS_SELECTOR, "tr[id^='vehicle_row']"
            )
            await asyncio.sleep(0.5)

            # Check if the vehicle is status 5
            on_scene_table_first_row.find_element(
                By.CSS_SELECTOR, ".building_list_fms_5"
            )

            # Go to the page of the vehicle to be cleared
            vehicle = on_scene_table_first_row.find_element(
                By.CSS_SELECTOR, "td:nth-child(2) > a"
            )
            vehicle_name = vehicle.text
            vehicle_url = vehicle.get_attribute("href")
            driver.get(vehicle_url)
            await asyncio.sleep(0.5)

            # Cancel transport button
            cancel_transport = driver.find_element(By.LINK_TEXT, "Cancel Transport")
            cancel_transport.click()
            cleared_count += 1
            await interaction.channel.send(
                content=f"Cancelled transport for {vehicle_name}"
            )
            await asyncio.sleep(0.5)

            try:
                # Back to mission button
                back_to_mission = driver.find_element(By.LINK_TEXT, "Back to mission")
                back_to_mission.click()
                await asyncio.sleep(0.5)
            except:
                await interaction.channel.send(
                    content=f"All {cleared_count} transport cleared"
                )
                break
        except:
            await interaction.channel.send(content="No status 5 unit found")
            break

    driver.quit()
