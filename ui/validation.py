"""Validation helpers for UI forms and payloads."""

from __future__ import annotations

import re


def validate_username(username: str) -> list[str]:
    errors: list[str] = []
    value = username.strip()
    if not value:
        return ["Username is required."]
    if len(value) < 3:
        errors.append("Username must be at least 3 characters.")
    if len(value) > 30:
        errors.append("Username must be 30 characters or fewer.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        errors.append("Username can contain only letters, numbers, dot, underscore, and hyphen.")
    return errors


def validate_password(password: str) -> list[str]:
    errors: list[str] = []
    if not password:
        return ["Password is required."]
    if len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if len(password) > 64:
        errors.append("Password must be 64 characters or fewer.")
    if password.lower() == password or password.upper() == password:
        errors.append("Password should include both uppercase and lowercase letters.")
    if not any(ch.isdigit() for ch in password):
        errors.append("Password should include at least one number.")
    return errors


def validate_registration(username: str, password: str, confirm_password: str) -> list[str]:
    errors = validate_username(username)
    errors.extend(validate_password(password))
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return errors


def validate_login(username: str, password: str) -> list[str]:
    errors = validate_username(username)
    if not password:
        errors.append("Password is required.")
    return errors


def validate_car_inputs(inputs: dict) -> list[str]:
    errors: list[str] = []
    age = int(inputs.get("vehicle_age", 0))
    km_driven = int(inputs.get("km_driven", 0))
    mileage = float(inputs.get("mileage", 0))
    engine = float(inputs.get("engine", 0))
    max_power = float(inputs.get("max_power", 0))
    seats = int(inputs.get("seats", 0))

    if age < 0 or age > 40:
        errors.append("Vehicle age must be between 0 and 40 years.")
    if km_driven < 0 or km_driven > 1_000_000:
        errors.append("Kilometres driven must be between 0 and 10,00,000.")
    if mileage <= 0:
        errors.append("Mileage must be greater than 0.")
    if mileage > 50:
        errors.append("Mileage looks unrealistic. Please enter a value up to 50 kmpl.")
    if engine < 500 or engine > 6000:
        errors.append("Engine capacity must be between 500cc and 6000cc.")
    if max_power < 20 or max_power > 800:
        errors.append("Max power must be between 20 and 800 bhp.")
    if seats < 2 or seats > 10:
        errors.append("Seats must be between 2 and 10.")

    if age <= 2 and km_driven > 150_000:
        errors.append("Km driven seems too high for a nearly new car.")
    if age >= 15 and km_driven < 5_000:
        errors.append("Km driven seems too low for an old car. Please verify.")

    for key in ("brand", "model", "fuel_type", "transmission_type", "seller_type"):
        if not inputs.get(key):
            errors.append(f"{key.replace('_', ' ').title()} is required.")

    return errors
