def run_disease_diagnosis():
    decision_tree = {
        "start": {
            "question": "Чи відчуваєте ви підвищену температуру? (так/ні): ",
            "так": "node_fever",
            "ні": "node_no_fever"
        },
        # якщо є підвищена температура
        "node_fever": {
            "question": "Чи є у вас кашель? (так/ні): ",
            "так": "node_cough",
            "ні": "node_no_cough"
        },
        "node_cough": {
            "question": "Чи є втрата смаку чи нюху? (так/ні): ",
            "так": "diagnosis_covid",
            "ні": "diagnosis_flu"
        },
        "node_no_cough": {
            "question": "Чи відчуваєте ви біль у м'язах та суглобах? (так/ні): ",
            "так": "diagnosis_flu",
            "ні": "diagnosis_unknown_infection"
        },
        # якщо немає підвищеної температури
        "node_no_fever": {
            "question": "Чи є у вас нежить та чхання? (так/ні): ",
            "так": "diagnosis_allergy",
            "ні": "diagnosis_cold"
        },
        # кінцеві діагнози
        "diagnosis_covid": {
            "result": "Можлива інфекція COVID-19. Зверніться до лікаря для проведення тестування."
        },
        "diagnosis_flu": {
            "result": "Можлива грипова інфекція. Рекомендується відпочинок, прийом жарознижуючих засобів і консультація лікаря."
        },
        "diagnosis_unknown_infection": {
            "result": "Можлива інша інфекційна хвороба. Зверніться до лікаря для уточнення діагнозу."
        },
        "diagnosis_allergy": {
            "result": "Можливі алергічні реакції. Зверніться до алерголога для визначення алергенів."
        },
        "diagnosis_cold": {
            "result": "Схоже, що у вас звичайна застуда. Рекомендується відпочинок та вживання рідини."
        }
    }
    
    current_node = "start"
    
    while True:
        node = decision_tree[current_node]
        if "result" in node:
            print("\nДіагноз:", node["result"])
            break
        
        answer = input(node["question"]).strip().lower()
        # Перевіряємо, чи введено "так" або "ні"
        if answer not in ["так", "ні"]:
            print("Будь ласка, введіть 'так' або 'ні'.")
            continue
        
        current_node = node[answer]

if __name__ == "__main__":
    run_disease_diagnosis()
