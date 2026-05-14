//
//     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄
//    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███
//    ████       ██     ██    ██  ████████
//   ██  ██      ██     ██    ██  ██ ██ ██
//   ██████      ██     ██    ██  ██ ▀▀ ██
//  ▄██  ██▄     ██      ██▄▄██   ██    ██
//  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀
//

import Foundation

enum Dzien: String, CaseIterable, Decodable, Identifiable, Sendable {
    case poniedzialek = "Poniedziałek"
    case wtorek = "Wtorek"
    case sroda = "Środa"
    case czwartek = "Czwartek"
    case piatek = "Piątek"

    // MARK: - Właściwości obliczeniowe

    var id: Self { self }
    var tytuł: String { rawValue }
    var opis: String { tytuł }
    var skróconyTytuł: String {
        switch self {
        case .poniedzialek: return "Pon."
        case .wtorek: return "Wt."
        case .sroda: return "Śr."
        case .czwartek: return "Czw."
        case .piatek: return "Pt."
        }
    }

    static var dzisiaj: Dzien {
        from(date: Date())
    }

    static func from(date: Date, calendar: Calendar = .current) -> Dzien {
        switch calendar.component(.weekday, from: date) {
        case 2: return .poniedzialek
        case 3: return .wtorek
        case 4: return .sroda
        case 5: return .czwartek
        case 6: return .piatek
        default:
            return .poniedzialek
        }
    }
}

struct Lekcja: Decodable {
    let id: String
    let dzien: Dzien
    let numer: Int
    let poczatek: String
    let koniec: String
    let przedmiot: String
    let nauczyciel: String?
    let sala: String?
    let oddzialy: String?
    let zastepstwo: String?
}

struct PlanLekcji: Decodable {
    let wygenerowano: String?
    let obowiazuje: String?
    let wygasa: String?
    let wolne: Bool
    let zastepstwa: Bool
    let lekcje: [Lekcja]
}
