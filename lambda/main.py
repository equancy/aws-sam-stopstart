#!/usr/bin/env python3
"""
Manages AWS instance state based on AUTO_START or AUTO_STOP tag
"""
import re
import boto3
import pendulum

AUTO_START_TAG = "AUTO_START"
AUTO_STOP_TAG = "AUTO_STOP"

TIME_PATTERN = re.compile(r"(?P<hour>\d{2})(?:\s+(?P<timezone>[A-Za-z]+/[A-Za-z]+))?$")
DAYS_RANGE_PATTERN = re.compile(r"^(?P<first>[A-Z]{3})-(?P<last>[A-Z]{3})\s+")
DAYS_LIST_PATTERN = re.compile(r"^(?P<days>[A-Z]{3}(?:,[A-Z]{3})*)\s+")
WEEKDAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]


def run_now(tag):
    time_match = TIME_PATTERN.search(tag)
    if time_match is None:
        raise ValueError("The schedule is not in correct format")

    timezone = time_match.group("timezone") or "UTC"
    now = pendulum.now(timezone)
    if time_match.group("hour") != now.format("HH"):
        return False

    # If No day is specified: run all days
    days_match = TIME_PATTERN.match(tag)
    if days_match:
        return True

    days_match = DAYS_RANGE_PATTERN.match(tag)
    if days_match:
        current_weekday_index = now.day_of_week
        first_index = WEEKDAYS.index(days_match.group("first"))
        last_index = WEEKDAYS.index(days_match.group("last"))
        if last_index < first_index:  # cross week schedule like FRI-MON
            return (
                current_weekday_index >= first_index
                or current_weekday_index <= last_index
            )
        else:
            return (
                current_weekday_index >= first_index
                and current_weekday_index <= last_index
            )

    days_match = DAYS_LIST_PATTERN.match(tag)
    if days_match:
        days = days_match.group("days").split(",")
        return WEEKDAYS[now.day_of_week] in days

    raise ValueError("The schedule is not in correct format")


def manage_instances_state(expected_state):
    ec2 = boto3.client("ec2")

    tag_name = AUTO_START_TAG if expected_state == "start" else AUTO_STOP_TAG
    current_instance_state = "stopped" if expected_state == "start" else "running"

    instance_filters = [
        {"Name": "tag-key", "Values": [tag_name]},
        {"Name": "instance-state-name", "Values": [current_instance_state]},
    ]
    instances_in_scope = ec2.describe_instances(Filters=instance_filters)
    instances_in_scope = instances_in_scope["Reservations"]

    has_failed = False
    for reservations in instances_in_scope:
        for instance in reservations["Instances"]:
            instance_id = instance["InstanceId"]
            try:
                for tag in instance["Tags"]:
                    if tag["Key"] == tag_name:
                        instance_schedule = tag["Value"]
                        break
                if run_now(instance_schedule):
                    if expected_state == "start":
                        print(f"Starting EC2 instance {instance_id}")
                        ec2.start_instances(InstanceIds=[instance_id])
                    else:
                        print(f"Stopping EC2 instance {instance_id}")
                        ec2.stop_instances(InstanceIds=[instance_id])

            except ValueError:
                print(
                    f"[WARNING] Auto {expected_state} tag for instance {instance_id} is not in correct format"
                )
            except Exception as error:
                print(
                    f"[ERROR] Failed to {expected_state} instance {instance_id}: {error}"
                )
                has_failed = True

    if has_failed:
        raise ValueError(
            f"Some instances did not {expected_state}. See logs for more information"
        )


def lambda_handler(event, context):
    print("Searching for instances to start...")
    manage_instances_state("start")
    print("Searching for instances to stop...")
    manage_instances_state("stop")
