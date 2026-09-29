"""
Geographic Filter module for PERSEPHONE Clinical Trials Intelligence.
Filters and annotates trial options based on patient location, geographic feasibility,
and site distribution.
"""

class GeographicFilter:
    """
    Handles site distance categorization and geographic eligibility filtering.
    """

    @classmethod
    def annotate_geography(cls, trials, patient_country="United States", patient_city="New York"):
        """
        Tags each trial with proximity metrics relative to patient residence.
        """
        p_country_low = (patient_country or "United States").lower()
        p_city_low = (patient_city or "").lower()

        annotated = []
        for t in trials:
            locations = t.get("locations", [])
            has_local = False
            has_national = False
            matched_sites = []

            for loc in locations:
                l_country = loc.get("country", "").lower()
                l_city = loc.get("city", "").lower()
                facility = loc.get("facility", "Clinical Trial Site")

                is_city_match = bool(p_city_low and (p_city_low in l_city or l_city in p_city_low))
                is_country_match = (p_country_low in l_country or l_country in p_country_low)

                if is_city_match:
                    has_local = True
                    matched_sites.append(f"{facility} ({loc.get('city')}, {loc.get('country')})")
                elif is_country_match:
                    has_national = True
                    matched_sites.append(f"{facility} ({loc.get('city', 'National')}, {loc.get('country')})")

            if has_local:
                category = "local"
            elif has_national:
                category = "national"
            elif locations:
                category = "international"
            else:
                category = "unspecified"

            item = dict(t)
            item["distanceCategory"] = category
            item["isLocal"] = has_local
            item["matchedSites"] = matched_sites[:3]
            annotated.append(item)

        return annotated

    @classmethod
    def filter_by_max_distance(cls, trials, allowed_categories=None):
        """
        Filters trials by distance category (e.g. ['local', 'national']).
        """
        if not allowed_categories:
            return trials
        allowed = set([c.lower() for c in allowed_categories])
        return [t for t in trials if t.get("distanceCategory", "").lower() in allowed]
