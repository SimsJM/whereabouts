"""Domain services for Whereabouts.

Later CB-61 tickets build the user, home, location, item and event services
here, on top of :mod:`whereabouts.db`. This package is intentionally empty in
the data-layer foundation ticket (CB-65); persistence itself lives in
:mod:`whereabouts.db` and the versioned files under ``migrations/``.
"""
