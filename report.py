def evaluate_range(value, ideal_min, ideal_max):
    if value < ideal_min:
        return "LOW"
    elif value > ideal_max:
        return "HIGH"
    else:
        return "OK"


def risk_label(score):
    if score <= 2:
        return "🟢 Low Risk"
    elif score <= 5:
        return "🟡 Medium Risk"
    else:
        return "🔴 High Risk"


def generate_report(data):
    report = {}
    issues = []
    suggestions = []
    risk_score = 0

    # ── ELBOW ──────────────────────────────────────────────
    elbow = data["elbow_angle"]
    elbow_status = evaluate_range(elbow, 160, 180)

    report["elbow"] = {
        "value": elbow,
        "status": elbow_status,
        "note": "Elbow angle is within legal and efficient range."
                if elbow_status == "OK"
                else f"Elbow at {elbow}° — possible bent arm or dropped elbow.",
        "fix": "Maintain current arm position."
               if elbow_status == "OK"
               else "Focus on straightening elbow through release. Do wall-press drills."
    }

    if elbow_status != "OK":
        issues.append("Elbow angle outside ideal range")
        suggestions.append("Wall-press arm extension drills")
        risk_score += 2

    # ── KNEE ───────────────────────────────────────────────
    knee = data["knee_angle"]
    knee_status = evaluate_range(knee, 145, 175)

    report["knee"] = {
        "value": knee,
        "status": knee_status,
        "note": "Front knee bracing is strong."
                if knee_status == "OK"
                else f"Knee at {knee}° — front leg collapsing at landing.",
        "fix": "Keep consistent knee drive."
               if knee_status == "OK"
               else "Strengthen quads and glutes. Practice landing stability drills."
    }

    if knee_status != "OK":
        issues.append("Front knee collapsing at landing")
        suggestions.append("Squat and lunge strengthening program")
        risk_score += 2

    # ── SHOULDER ───────────────────────────────────────────
    shoulder = data["shoulder_alignment"]

    report["shoulder"] = {
        "value": shoulder,
        "note": "Shoulder alignment is correct."
                if shoulder == "straight"
                else "Shoulder is open — losing power and accuracy.",
        "fix": "Maintain alignment."
               if shoulder == "straight"
               else "Record side view and check alignment against target line."
    }

    if shoulder != "straight":
        issues.append("Open shoulder alignment")
        suggestions.append("Alignment target drills with stump markers")
        risk_score += 2

    # ── FOLLOW THROUGH ─────────────────────────────────────
    balance = data["follow_balance"]

    report["follow"] = {
        "value": balance,
        "note": "Follow-through balance is controlled."
                if balance == "stable"
                else "Unstable follow-through — injury risk at lower back and knee.",
        "fix": "Maintain current finish."
               if balance == "stable"
               else "Practice single-leg balance holds. Slow down follow-through in training."
    }

    if balance != "stable":
        issues.append("Unstable follow-through")
        suggestions.append("Single-leg stability and core strengthening")
        risk_score += 1

    # ── ARM TYPE ───────────────────────────────────────────
    arm_type = data.get("arm_type", "Unknown")
    report["arm_type"] = arm_type

    # ── SUMMARY ────────────────────────────────────────────
    report["summary"] = {
        "score": max(1, 10 - risk_score),
        "risk": risk_label(risk_score),
        "issues": issues,
        "suggestions": suggestions
    }

    return report