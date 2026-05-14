//
//     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄
//    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███
//    ████       ██     ██    ██  ████████
//   ██  ██      ██     ██    ██  ██ ██ ██
//   ██████      ██     ██    ██  ██ ▀▀ ██
//  ▄██  ██▄     ██      ██▄▄██   ██    ██
//  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀
//

import SwiftUI

struct PersonalizationView: View {

    // MARK: - Typy pomocnicze

    private enum AktywnyArkusz: Identifiable {
        case nauczyciel
        case oddział
        case tekst(ArkuszTekstowy)

        var id: String {
            switch self {
            case .nauczyciel:
                return "nauczyciel"
            case .oddział:
                return "oddział"
            case .tekst(let arkusz):
                return "tekst-\(arkusz.rawValue)"
            }
        }
    }

    private enum ArkuszTekstowy: String {
        case numerekUcznia
        case grupaZajęćLekcyjnych
        case grupaWychowaniaFizycznego
        case grupaZajęćPraktycznych

        var tytułNawigacji: String {
            switch self {
            case .numerekUcznia:
                return "Numer w dzienniku"
            case .grupaZajęćLekcyjnych:
                return "Grupa lekcyjna"
            case .grupaWychowaniaFizycznego:
                return "Grupa WF"
            case .grupaZajęćPraktycznych:
                return "Zajęcia praktyczne"
            }
        }

        var tytułSelektora: String {
            switch self {
            case .numerekUcznia:
                return "Numer"
            case .grupaZajęćLekcyjnych:
                return "Grupa lekcyjna"
            case .grupaWychowaniaFizycznego:
                return "Grupa WF"
            case .grupaZajęćPraktycznych:
                return "Grupa zajęć praktycznych"
            }
        }

        var elementy: [String] {
            switch self {
            case .numerekUcznia:
                return Dane.dostępneNumery
            case .grupaZajęćLekcyjnych:
                return Dane.grupyZajęćLekcyjnych
            case .grupaWychowaniaFizycznego:
                return Dane.grupyWychowaniaFizycznego
            case .grupaZajęćPraktycznych:
                return Dane.grupyZajęćPraktycznych
            }
        }

        var rozmiaryArkusza: Set<PresentationDetent> {
            switch self {
            case .numerekUcznia:
                return [.fraction(0.4), .medium]
            case .grupaZajęćLekcyjnych, .grupaWychowaniaFizycznego, .grupaZajęćPraktycznych:
                return [.fraction(0.4)]
            }
        }

        func etykietaWartości(wartość: String) -> String {
            if self == .grupaWychowaniaFizycznego {
                return Dane.etykietyGrupWychowaniaFizycznego[wartość] ?? wartość
            }

            return wartość
        }
    }

    private enum Dane {
        static let wartośćBrak = "Brak"
        static let wartośćKliknijTutaj = "Kliknij tutaj"
        static let wartośćBrakDanych = "Brak danych"

        static let dostępneNumery =
            [wartośćBrak] + Array(1...40).map(String.init)

        static let grupyZajęćLekcyjnych =
            [wartośćBrak, "1/2", "2/2"]

        static let grupyZajęćPraktycznych =
            [wartośćBrak, "1/3", "2/3", "3/3"]

        static let grupyWychowaniaFizycznego =
            [wartośćBrak, "j1", "j2"]

        static let etykietyGrupWychowaniaFizycznego: [String: String] = [
            "j1": "1/2",
            "j2": "2/2"
        ]
    }

    // MARK: - Właściwości

    let czyTrybKonfiguracji: Bool

    @Environment(AuthSessionViewModel.self) private var modelSesji
    @State private var modelWidoku = PersonalizationViewModel()

    @AppStorage(KluczeUstawień.oddział) private var oddział: String = ""
    @AppStorage(KluczeUstawień.identyfikatorOddziału) private var identyfikatorOddziału: String = ""
    @AppStorage(KluczeUstawień.nauczyciel) private var nauczyciel: String = ""
    @AppStorage(KluczeUstawień.identyfikatorNauczyciela) private var identyfikatorNauczyciela: String = ""
    @AppStorage(KluczeUstawień.numerekUcznia) private var numerekUcznia: String = ""
    @AppStorage(KluczeUstawień.grupaZajęćLekcyjnych) private var grupaZajęćLekcyjnych: String = ""
    @AppStorage(KluczeUstawień.grupaZajęćPraktycznych) private var grupaZajęćPraktycznych: String = ""
    @AppStorage(KluczeUstawień.grupaWychowaniaFizycznego) private var grupaWychowaniaFizycznego: String = ""
    @AppStorage(KluczeUstawień.religia) private var religia: Bool = true
    @AppStorage(KluczeUstawień.edukacjaZdrowotna) private var edukacjaZdrowotna: Bool = true
    @AppStorage(KluczeUstawień.czyKonfiguracjaZakończona) private var czyKonfiguracjaZakończona = false

    @State private var aktywnyArkusz: AktywnyArkusz?
    @State private var czyPokazaćPotwierdzenieUsunięciaKonta = false
    @State private var wybranyIdentyfikatorWSelektorze: String = ""
    @State private var wybranaWartośćTekstowaWSelektorze: String = Dane.wartośćBrak

    // MARK: - Inicjalizacja

    init(czyTrybKonfiguracji: Bool = false) {
        self.czyTrybKonfiguracji = czyTrybKonfiguracji
    }

    // MARK: - Właściwości obliczeniowe

    private var wybranoOddział: Bool { !identyfikatorOddziału.isEmpty }
    private var wybranoNauczyciela: Bool { !identyfikatorNauczyciela.isEmpty }

    private var tekstWybranegoOddziału: String {
        tekstWybranejRoli(
            identyfikator: identyfikatorOddziału,
            pobierzOpcję: modelWidoku.opcjaOddziału(oId:)
        )
    }

    private var tekstWybranegoNauczyciela: String {
        tekstWybranejRoli(
            identyfikator: identyfikatorNauczyciela,
            pobierzOpcję: modelWidoku.opcjaNauczyciela(oId:)
        )
    }

    private var wartośćNumerku: String { numerekUcznia.isEmpty ? Dane.wartośćBrak : numerekUcznia }
    private var wartośćGrupyLekcyjnej: String { grupaZajęćLekcyjnych.isEmpty ? Dane.wartośćBrak : grupaZajęćLekcyjnych }
    private var wartośćGrupyPraktyk: String { grupaZajęćPraktycznych.isEmpty ? Dane.wartośćBrak : grupaZajęćPraktycznych }

    private var wartośćGrupyWF: String {
        if grupaWychowaniaFizycznego.isEmpty { return Dane.wartośćBrak }
        return Dane.etykietyGrupWychowaniaFizycznego[grupaWychowaniaFizycznego] ?? grupaWychowaniaFizycznego
    }

    private var czyPrzyciskDalejJestNieaktywny: Bool {
        !wybranoOddział && !wybranoNauczyciela
    }

    private var powiązanieBłęduSesji: Binding<Bool> {
        Binding(
            get: { modelSesji.błąd != nil },
            set: { czyJestPrezentowany in
                if !czyJestPrezentowany {
                    modelSesji.wyczyśćBłąd()
                }
            }
        )
    }

    private func bindingWartościTekstowej(dla arkusz: ArkuszTekstowy) -> Binding<String> {
        switch arkusz {
        case .numerekUcznia:
            return $numerekUcznia
        case .grupaZajęćLekcyjnych:
            return $grupaZajęćLekcyjnych
        case .grupaWychowaniaFizycznego:
            return $grupaWychowaniaFizycznego
        case .grupaZajęćPraktycznych:
            return $grupaZajęćPraktycznych
        }
    }

    // MARK: - Widok

    var body: some View {
        Form {
            sekcjeWyboruRoli

            if wybranoOddział {
                sekcjeDlaUcznia
            }

            if czyTrybKonfiguracji {
                sekcjaUsuwaniaKonta
            }
        }
        .disabled(modelSesji.czyŁaduje)
        .animation(.easeInOut(duration: 0.2), value: wybranoOddział || wybranoNauczyciela)
        .interactiveDismissDisabled(czyPrzyciskDalejJestNieaktywny && czyTrybKonfiguracji)
        .navigationTitle("Personalizacja")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            if !czyTrybKonfiguracji {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Dalej") { czyKonfiguracjaZakończona = true }
                        .disabled(czyPrzyciskDalejJestNieaktywny)
                }
            }
        }
        .sheet(item: $aktywnyArkusz) { arkusz in
            zawartośćArkusza(arkusz: arkusz)
        }
        .task {
            await modelWidoku.załaduj()
        }
        .alert(
            "Wystąpił błąd",
            isPresented: Binding(
                get: { modelWidoku.błąd != nil },
                set: { czyJestPrezentowany in
                    if !czyJestPrezentowany {
                        modelWidoku.wyczyśćBłąd()
                    }
                }
            )
        ) {
            Button("OK") {
                modelWidoku.wyczyśćBłąd()
            }
        } message: {
            Text(modelWidoku.błąd ?? "")
        }
        .alert("Wystąpił błąd", isPresented: powiązanieBłęduSesji) {
            Button("OK") {
                modelSesji.wyczyśćBłąd()
            }
        } message: {
            Text(modelSesji.błąd ?? "")
        }
        .alert("Usunąć konto?", isPresented: $czyPokazaćPotwierdzenieUsunięciaKonta) {
            Button("Anuluj", role: .cancel) {
            }
            Button("Usuń konto", role: .destructive) {
                Task {
                    await modelSesji.usuńKonto()
                }
            }
        } message: {
            Text("Ta operacja usunie Twoje konto oraz preferencje z nim powiązane. Nie będzie można jej cofnąć.")
        }
    }

    // MARK: - Sekcje formularza
    @ViewBuilder
    private var sekcjeWyboruRoli: some View {
        if !wybranoNauczyciela {
            sekcjaWyboru(
                nagłówek: "Personalizacja ucznia",
                stopka: "Na podstawie tego wyboru będzie Tobie wyświetlany odpowiedni plan lekcji oraz dostarczane zastępstwa przypisane do Twojego oddziału.",
                ikona: "puzzlepiece.extension",
                tytuł: "Jesteś uczniem?",
                wartość: tekstWybranegoOddziału,
                akcja: {
                    otwórzSelektorIdentyfikatora(
                        arkusz: .oddział,
                        aktualnyIdentyfikator: identyfikatorOddziału,
                        opcje: modelWidoku.dostępneOddziały
                    )
                }
            )
        }

        if !wybranoOddział {
            sekcjaWyboru(
                nagłówek: "Personalizacja nauczyciela",
                stopka: "Na podstawie tego wyboru będzie Tobie wyświetlany odpowiedni plan lekcji oraz dostarczane zastępstwa przypisane do Twojego nazwiska.",
                ikona: "puzzlepiece",
                tytuł: "Jesteś nauczycielem?",
                wartość: tekstWybranegoNauczyciela,
                akcja: {
                    otwórzSelektorIdentyfikatora(
                        arkusz: .nauczyciel,
                        aktualnyIdentyfikator: identyfikatorNauczyciela,
                        opcje: modelWidoku.dostępniNauczyciele
                    )
                }
            )
        }
    }

    @ViewBuilder
    private var sekcjeDlaUcznia: some View {
        sekcjaWyboru(
            stopka: "Wybór numeru w dzienniku umożliwi otrzymywanie powiadomień o szczęśliwym numerku. ",
            ikona: "numbers",
            tytuł: "Numer w dzienniku",
            wartość: wartośćNumerku,
            akcja: { otwórzArkuszTekstowy(arkusz: .numerekUcznia) }
        )

        Section(
            footer: Text("Wybór grup nie jest obowiązkowy. Na podstawie tych wyborów będzie wyświetlany Tobie zmodyfikowany plan lekcji oddziału, który wybierzesz.")
        ) {
            przyciskWyboru(
                akcja: { otwórzArkuszTekstowy(arkusz: .grupaZajęćLekcyjnych) },
                ikona: "person.3.fill",
                tytuł: "Grupa zajęć lekcyjnych",
                wartość: wartośćGrupyLekcyjnej
            )

            przyciskWyboru(
                akcja: { otwórzArkuszTekstowy(arkusz: .grupaWychowaniaFizycznego) },
                ikona: "person.3",
                tytuł: "Grupa zajęć WF",
                wartość: wartośćGrupyWF
            )
        }

        sekcjaWyboru(
            stopka: "Dotyczy tylko oddziałów, które uczęszczają na zajęcia praktyczne podzielone na trzy grupy.",
            ikona: "rectangle.3.group.dashed",
            tytuł: "Grupa zajęć praktycznych",
            wartość: wartośćGrupyPraktyk,
            akcja: { otwórzArkuszTekstowy(arkusz: .grupaZajęćPraktycznych) }
        )

        Section(
            footer: Text("Jeżeli nie chcesz, aby Twój plan lekcji zawierał dane o tych zajęciach, odznacz odpowiednie opcje.")
        ) {
            Toggle(isOn: $religia) {
                Label { Text("Religia") } icon: {
                    Image(systemName: "cross")
                        .foregroundStyle(.secondary)
                }
            }

            Toggle(isOn: $edukacjaZdrowotna) {
                Label { Text("Edukacja zdrowotna") } icon: {
                    Image(systemName: "staroflife")
                        .foregroundStyle(.secondary)
                }
            }
        }
    }

    private var sekcjaUsuwaniaKonta: some View {
        Section(
            footer: Text("Twoje konto zostanie usunięte, a konfiguracja aplikacji zostanie wyczyszczona. Ze względu na zastosowane ograniczenia firmy Apple zachowane zostanie jedynie Twoja nazwa oraz identyfikator.")
        ) {
            Button(role: .destructive) {
                czyPokazaćPotwierdzenieUsunięciaKonta = true
            } label: {
                Label("Usuń konto", systemImage: "trash")
            }
        }
    }

    // MARK: - Budowanie widoków
    /// Tworzy sekcję formularza zawierającą pojedynczy wiersz wyboru.
    private func sekcjaWyboru(
        nagłówek: String? = nil,
        stopka: String,
        ikona: String,
        tytuł: String,
        wartość: String,
        akcja: @escaping () -> Void
    ) -> some View {
        Section(
            header: nagłówek.map(Text.init),
            footer: Text(stopka)
        ) {
            przyciskWyboru(akcja: akcja, ikona: ikona, tytuł: tytuł, wartość: wartość)
        }
    }

    /// Buduje wiersz przycisku używany w sekcjach konfiguracji.
    private func przyciskWyboru(
        akcja: @escaping () -> Void,
        ikona: String,
        tytuł: String,
        wartość: String
    ) -> some View {
        Button(action: akcja) {
            HStack {
                Image(systemName: ikona)
                    .foregroundStyle(.secondary)
                Text(tytuł)
                Spacer()
                Text(wartość)
                    .foregroundStyle(.secondary)
                Image(systemName: "chevron.right")
                    .foregroundStyle(.secondary)
            }
        }
        .buttonStyle(.plain)
    }

    // MARK: - Funkcje pomocnicze
    private func tekstWybranejRoli(
        identyfikator: String,
        pobierzOpcję: (String) -> PersonalizationViewModel.OpcjaListy?
    ) -> String {
        guard !identyfikator.isEmpty else { return Dane.wartośćKliknijTutaj }
        return pobierzOpcję(identyfikator)?.nazwa ?? Dane.wartośćBrakDanych
    }

    /// Tworzy wspólny kontener nawigacyjny dla arkuszy wyboru.
    private func kontenerArkusza<Content: View>(
        tytułNawigacji: String,
        rozmiaryArkusza: Set<PresentationDetent>,
        czyMożnaZatwierdzić: Bool = true,
        poZatwierdzeniu: @escaping () -> Void,
        @ViewBuilder zawartość: () -> Content
    ) -> some View {
        NavigationStack {
            zawartość()
                .padding(.horizontal)
                .navigationTitle(tytułNawigacji)
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem {
                        Button("Gotowe", systemImage: "checkmark", action: poZatwierdzeniu)
                            .disabled(!czyMożnaZatwierdzić)
                    }
                }
        }
        .presentationDetents(rozmiaryArkusza)
        .presentationDragIndicator(.hidden)
    }

    // MARK: - Akcje arkuszy
    /// Otwiera arkusz wyboru elementu identyfikowanego przez ID.
    private func otwórzSelektorIdentyfikatora(
        arkusz: AktywnyArkusz,
        aktualnyIdentyfikator: String,
        opcje: [PersonalizationViewModel.OpcjaListy]
    ) {
        wybranyIdentyfikatorWSelektorze = opcje.contains(where: { $0.id == aktualnyIdentyfikator }) ? aktualnyIdentyfikator : ""
        aktywnyArkusz = arkusz
    }

    /// Otwiera arkusz wyboru dla wartości tekstowych (np. numer, grupa).
    private func otwórzArkuszTekstowy(arkusz: ArkuszTekstowy) {
        let aktualnaWartość = bindingWartościTekstowej(dla: arkusz).wrappedValue
        wybranaWartośćTekstowaWSelektorze =
            arkusz.elementy.contains(aktualnaWartość) && !aktualnaWartość.isEmpty
            ? aktualnaWartość
            : Dane.wartośćBrak
        aktywnyArkusz = .tekst(arkusz)
    }

    // MARK: - Akcje zapisu
    private func zatwierdźWybórNauczyciela() {
        defer { aktywnyArkusz = nil }

        guard let wybranyNauczyciel = modelWidoku.opcjaNauczyciela(oId: wybranyIdentyfikatorWSelektorze) else {
            return
        }

        if wybranyNauczyciel.id.isEmpty {
            wyczyśćNauczyciela()
            return
        }

        nauczyciel = wybranyNauczyciel.nazwa
        identyfikatorNauczyciela = wybranyNauczyciel.id

        wyczyśćDaneOddziału()
        wyczyśćDaneDodatkoweUcznia()
    }

    private func zatwierdźWybórOddziału() {
        defer { aktywnyArkusz = nil }

        guard let wybranyOddział = modelWidoku.opcjaOddziału(oId: wybranyIdentyfikatorWSelektorze) else {
            return
        }

        if wybranyOddział.id.isEmpty {
            wyczyśćDaneOddziału()
            wyczyśćDaneDodatkoweUcznia()
            przywróćDomyślneUstawieniaPrzełączników()
            return
        }

        oddział = wybranyOddział.nazwa
        identyfikatorOddziału = wybranyOddział.id

        wyczyśćNauczyciela()
    }

    private func zatwierdźArkuszTekstowy(arkusz: ArkuszTekstowy) {
        bindingWartościTekstowej(dla: arkusz).wrappedValue =
            wybranaWartośćTekstowaWSelektorze == Dane.wartośćBrak
            ? ""
            : wybranaWartośćTekstowaWSelektorze
        aktywnyArkusz = nil
    }

    private func wyczyśćNauczyciela() {
        nauczyciel = ""
        identyfikatorNauczyciela = ""
    }

    private func wyczyśćDaneOddziału() {
        oddział = ""
        identyfikatorOddziału = ""
    }

    private func wyczyśćDaneDodatkoweUcznia() {
        numerekUcznia = ""
        grupaZajęćLekcyjnych = ""
        grupaWychowaniaFizycznego = ""
        grupaZajęćPraktycznych = ""
    }

    private func przywróćDomyślneUstawieniaPrzełączników() {
        religia = true
        edukacjaZdrowotna = true
    }

    // MARK: - Arkusze
    @ViewBuilder
    private func zawartośćArkusza(arkusz: AktywnyArkusz) -> some View {
        switch arkusz {
        case .nauczyciel:
            arkuszDlaListyElementów(
                tytułNawigacji: "Wybierz nauczyciela",
                tytułSelektora: "Nauczyciel",
                elementy: modelWidoku.dostępniNauczyciele,
                wybranyIdentyfikator: $wybranyIdentyfikatorWSelektorze,
                czyMożnaZatwierdzić: modelWidoku.czyListaNauczycieliJestZaładowana,
                poZatwierdzeniu: zatwierdźWybórNauczyciela
            )

        case .oddział:
            arkuszDlaListyElementów(
                tytułNawigacji: "Wybierz klasę",
                tytułSelektora: "Klasa",
                elementy: modelWidoku.dostępneOddziały,
                wybranyIdentyfikator: $wybranyIdentyfikatorWSelektorze,
                czyMożnaZatwierdzić: modelWidoku.czyListaOddziałówJestZaładowana,
                poZatwierdzeniu: zatwierdźWybórOddziału
            )

        case .tekst(let arkuszTekstowy):
            arkuszDlaListyTekstów(
                tytułNawigacji: arkuszTekstowy.tytułNawigacji,
                tytułSelektora: arkuszTekstowy.tytułSelektora,
                elementy: arkuszTekstowy.elementy,
                wybranaWartość: $wybranaWartośćTekstowaWSelektorze,
                rozmiaryArkusza: arkuszTekstowy.rozmiaryArkusza,
                etykietaWartości: arkuszTekstowy.etykietaWartości,
                poZatwierdzeniu: { zatwierdźArkuszTekstowy(arkusz: arkuszTekstowy) }
            )
        }
    }

    /// Tworzy arkusz z pickerem dla elementów identyfikowanych przez ID.
    private func arkuszDlaListyElementów(
        tytułNawigacji: String,
        tytułSelektora: String,
        elementy: [PersonalizationViewModel.OpcjaListy],
        wybranyIdentyfikator: Binding<String>,
        rozmiaryArkusza: Set<PresentationDetent> = [.fraction(0.4)],
        czyMożnaZatwierdzić: Bool = true,
        poZatwierdzeniu: @escaping () -> Void
    ) -> some View {
        kontenerArkusza(
            tytułNawigacji: tytułNawigacji,
            rozmiaryArkusza: rozmiaryArkusza,
            czyMożnaZatwierdzić: czyMożnaZatwierdzić,
            poZatwierdzeniu: poZatwierdzeniu
        ) {
            Picker(tytułSelektora, selection: wybranyIdentyfikator) {
                ForEach(elementy) { element in
                    Text(element.nazwa).tag(element.id)
                }
            }
            .pickerStyle(.wheel)
        }
    }

    /// Tworzy arkusz z pickerem dla listy wartości tekstowych.
    private func arkuszDlaListyTekstów(
        tytułNawigacji: String,
        tytułSelektora: String,
        elementy: [String],
        wybranaWartość: Binding<String>,
        rozmiaryArkusza: Set<PresentationDetent> = [.fraction(0.4)],
        etykietaWartości: @escaping (String) -> String = { $0 },
        poZatwierdzeniu: @escaping () -> Void
    ) -> some View {
        kontenerArkusza(
            tytułNawigacji: tytułNawigacji,
            rozmiaryArkusza: rozmiaryArkusza,
            poZatwierdzeniu: poZatwierdzeniu
        ) {
            Picker(tytułSelektora, selection: wybranaWartość) {
                ForEach(elementy, id: \.self) { element in
                    Text(etykietaWartości(element)).tag(element)
                }
            }
            .pickerStyle(.wheel)
        }
    }
}
