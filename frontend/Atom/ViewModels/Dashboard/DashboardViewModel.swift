//
//     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄
//    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███
//    ████       ██     ██    ██  ████████
//   ██  ██      ██     ██    ██  ██ ██ ██
//   ██████      ██     ██    ██  ██ ▀▀ ██
//  ▄██  ██▄     ██      ██▄▄██   ██    ██
//  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀
//

import Combine
import Foundation
import Observation

@MainActor
@Observable
final class DashboardViewModel {
    // MARK: - Zależności

    private let kalendarz: Calendar
    private let modelPlanu: TimetableViewModel
    private let modelNumerków: NumbersViewModel

    // MARK: - Stan

    var aktualnaData = Date()

    // MARK: - Inicjalizacja

    init(
        kalendarz: Calendar = .current,
        modelPlanu: TimetableViewModel? = nil,
        modelNumerków: NumbersViewModel? = nil
    ) {
        self.kalendarz = kalendarz
        self.modelPlanu = modelPlanu ?? TimetableViewModel()
        self.modelNumerków = modelNumerków ?? NumbersViewModel()
    }

    // MARK: - Właściwości obliczeniowe

    var wybranyDzień: Dzien {
        Dzien.from(date: aktualnaData, calendar: kalendarz)
    }

    var kluczDnia: Date {
        kalendarz.startOfDay(for: aktualnaData)
    }

    var grupyLekcji: [GrupaLekcjiWidoku] {
        GrupaLekcjiWidoku.utwórz(z: modelPlanu.lekcje)
    }

    var opisNumerków: String {
        modelNumerków.opisNumerków
    }

    var czyŁadujeNumerki: Bool {
        modelNumerków.czyŁaduje
    }

    var czyŁadujePlan: Bool {
        modelPlanu.czyŁaduje
    }

    var tekstBłęduNumerków: String? {
        modelNumerków.błąd
    }

    var tekstBłęduPlanu: String? {
        modelPlanu.błąd
    }

    var czyDaneZastępstwDostępne: Bool {
        modelPlanu.czyDaneZastępstwDostępne
    }

    var czyWolne: Bool {
        modelPlanu.czyWolne
    }

    var czyPokazaćBrakLekcji: Bool {
        modelPlanu.lekcje.isEmpty || czyPoLekcjachDzisiaj
    }

    var komunikatPlanu: String {
        if czyWolne {
            return "Wygląda na to, że dzisiaj dzień wolny od zajęć!"
        }

        return "Wygląda na to, że na dzisiaj to już wszystko!"
    }

    // MARK: - Akcje

    func załadujNumerki(pomińCache: Bool = false) async {
        await modelNumerków.załaduj(pomińCache: pomińCache)
    }

    func załadujPlan(
        identyfikator: String?,
        grupy: [String]?,
        religia: Bool,
        edukacjaZdrowotna: Bool,
        pomińCache: Bool = false
    ) async {
        await modelPlanu.załaduj(
            identyfikator: identyfikator,
            grupy: grupy,
            dzien: wybranyDzień,
            religia: religia,
            edukacjaZdrowotna: edukacjaZdrowotna,
            pomińCache: pomińCache
        )
    }

    func odświeżAktualnąDatę() {
        aktualnaData = Date()
    }

    func czyAktywna(grupa: GrupaLekcjiWidoku) -> Bool {
        guard
            !kalendarz.isDateInWeekend(aktualnaData),
            let zakres = zakresCzasu(
                poczatek: grupa.poczatek,
                koniec: grupa.koniec,
                względem: aktualnaData
            )
        else {
            return false
        }

        return aktualnaData >= zakres.start && aktualnaData <= zakres.end
    }

    func opisPozostałegoCzasu(dla grupa: GrupaLekcjiWidoku) -> String? {
        guard
            !kalendarz.isDateInWeekend(aktualnaData),
            let zakres = zakresCzasu(
                poczatek: grupa.poczatek,
                koniec: grupa.koniec,
                względem: aktualnaData
            ),
            aktualnaData >= zakres.start,
            aktualnaData <= zakres.end
        else {
            return nil
        }

        let minuty = kalendarz.dateComponents([.minute], from: aktualnaData, to: zakres.end).minute ?? 0
        return minuty > 0 ? "\(minuty) min" : "< 1 min"
    }

    func opisCzasuDoRozpoczęcia(dla grupa: GrupaLekcjiWidoku) -> String? {
        guard
            !kalendarz.isDateInWeekend(aktualnaData),
            !grupyLekcji.contains(where: czyAktywna),
            let indeksGrupy = grupyLekcji.firstIndex(where: { $0.id == grupa.id }),
            indeksGrupy > 0
        else {
            return nil
        }

        let poprzedniaGrupa = grupyLekcji[indeksGrupy - 1]

        guard
            let zakresPoprzedniejLekcji = zakresCzasu(
                poczatek: poprzedniaGrupa.poczatek,
                koniec: poprzedniaGrupa.koniec,
                względem: aktualnaData
            ),
            let zakresAktualnejGrupy = zakresCzasu(
                poczatek: grupa.poczatek,
                koniec: grupa.koniec,
                względem: aktualnaData
            ),
            aktualnaData > zakresPoprzedniejLekcji.end,
            aktualnaData < zakresAktualnejGrupy.start
        else {
            return nil
        }

        let minuty = kalendarz.dateComponents(
            [.minute],
            from: aktualnaData,
            to: zakresAktualnejGrupy.start
        ).minute ?? 0

        return minuty > 0 ? "\(minuty) min" : "< 1 min"
    }

    // MARK: - Prywatne

    private var czyPoLekcjachDzisiaj: Bool {
        guard
            let ostatniaGrupa = grupyLekcji.last,
            let zakres = zakresCzasu(
                poczatek: ostatniaGrupa.poczatek,
                koniec: ostatniaGrupa.koniec,
                względem: aktualnaData
            )
        else {
            return false
        }

        return !kalendarz.isDateInWeekend(aktualnaData) && aktualnaData > zakres.end
    }

    private func zakresCzasu(
        poczatek: String,
        koniec: String,
        względem data: Date
    ) -> (start: Date, end: Date)? {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        formatter.locale = Locale(identifier: "pl_PL")

        guard
            let dataPoczątku = formatter.date(from: poczatek),
            let dataKońca = formatter.date(from: koniec),
            let start = kalendarz.date(
                bySettingHour: kalendarz.component(.hour, from: dataPoczątku),
                minute: kalendarz.component(.minute, from: dataPoczątku),
                second: 0,
                of: data
            ),
            let end = kalendarz.date(
                bySettingHour: kalendarz.component(.hour, from: dataKońca),
                minute: kalendarz.component(.minute, from: dataKońca),
                second: 0,
                of: data
            )
        else {
            return nil
        }

        return (start, end)
    }
}
