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

struct TimetableView: View {
    @Environment(\.colorScheme) private var schematKoloru

    @State private var modelWidoku = TimetableViewModel()

    @Binding private var wybranyDzień: Dzien
    @State private var czyPokazaćZarządzanieKontem = false
    @State private var czyRozwiniętoInformacjePlanu = false

    @AppStorage(KluczeUstawień.identyfikatorOddziału) private var identyfikatorOddziału: String = ""
    @AppStorage(KluczeUstawień.identyfikatorNauczyciela) private var identyfikatorNauczyciela: String = ""
    @AppStorage(KluczeUstawień.grupaZajęćLekcyjnych) private var grupaZajęćLekcyjnych: String = ""
    @AppStorage(KluczeUstawień.grupaZajęćPraktycznych) private var grupaZajęćPraktycznych: String = ""
    @AppStorage(KluczeUstawień.grupaWychowaniaFizycznego) private var grupaWychowaniaFizycznego: String = ""
    @AppStorage(KluczeUstawień.religia) private var religia = true
    @AppStorage(KluczeUstawień.edukacjaZdrowotna) private var edukacjaZdrowotna = true

    private var identyfikator: String? {
        let id = !identyfikatorNauczyciela.isEmpty ? identyfikatorNauczyciela : identyfikatorOddziału
        return id.isEmpty ? nil : id
    }

    private var wybraneGrupy: [String]? {
        let grupy = [
            grupaZajęćLekcyjnych,
            grupaZajęćPraktycznych,
            grupaWychowaniaFizycznego
        ].filter { !$0.isEmpty }

        return grupy.isEmpty ? nil : grupy
    }

    private var kluczOdświeżania: [String] {
        [
            identyfikator ?? "",
            wybranyDzień.rawValue,
            grupaZajęćLekcyjnych,
            grupaZajęćPraktycznych,
            grupaWychowaniaFizycznego,
            religia.description,
            edukacjaZdrowotna.description
        ]
    }

    private func odśwież() async {
        await modelWidoku.załaduj(
            identyfikator: identyfikator,
            grupy: wybraneGrupy,
            zastepstwa: true,
            dzien: wybranyDzień,
            religia: religia,
            edukacjaZdrowotna: edukacjaZdrowotna,
            pomińCache: true
        )
    }

    private var czyPlanNauczyciela: Bool {
        !identyfikatorNauczyciela.isEmpty
    }

    init(wybranyDzień: Binding<Dzien>) {
        self._wybranyDzień = wybranyDzień
    }

    var body: some View {
        głównaZawartość
        .tłoAtomu(schematKoloru: schematKoloru)
        .navigationTitle("Plan lekcji")
        .navigationSubtitle(wybranyDzień.tytuł)
        .toolbarTitleDisplayMode(.inlineLarge)
        .toolbar {
            ToolbarItem {
                Button {
                    czyPokazaćZarządzanieKontem = true
                } label: {
                    Image(systemName: "person.crop.circle")
                        .font(.title2)
                }
            }
        }
        .arkuszZarządzaniaKontem(czyPokazać: $czyPokazaćZarządzanieKontem)
        .task(id: kluczOdświeżania) {
            await modelWidoku.załaduj(
                identyfikator: identyfikator,
                grupy: wybraneGrupy,
                zastepstwa: true,
                dzien: wybranyDzień,
                religia: religia,
                edukacjaZdrowotna: edukacjaZdrowotna
            )
        }
    }

    // MARK: - Sekcje

    @ViewBuilder
    private var głównaZawartość: some View {
        if modelWidoku.czyŁaduje && modelWidoku.lekcje.isEmpty || modelWidoku.błąd != nil || modelWidoku.lekcje.isEmpty {
            GeometryReader { geometria in
                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {
                        selektorDni
                        if !modelWidoku.czyDaneZastępstwDostępne {
                            kartaInformacjiOBrakuZastępstw
                        }
                        zawartośćPlanu
                        stopkaInformacjiPlanu
                    }
                    .padding()
                    .frame(minHeight: geometria.size.height, alignment: .top)
                }
                .refreshable {
                    await odśwież()
                }
            }
        } else {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    selektorDni
                    if !modelWidoku.czyDaneZastępstwDostępne {
                        kartaInformacjiOBrakuZastępstw
                    }
                    zawartośćPlanu
                    stopkaInformacjiPlanu
                }
                .padding()
            }
            .refreshable {
                await odśwież()
            }
        }
    }

    @ViewBuilder
    private var zawartośćPlanu: some View {
        if modelWidoku.czyŁaduje && modelWidoku.lekcje.isEmpty {
            ProgressView()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let błąd = modelWidoku.błąd {
            ContentUnavailableView(
                "Nie udało się pobrać planu lekcji",
                systemImage: "exclamationmark.bubble.fill",
                description: Text(błąd)
            )
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if modelWidoku.lekcje.isEmpty {
            ContentUnavailableView(
                "Brak opublikowanego planu lekcji",
                systemImage: "text.page.slash.fill"
            )
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else {
            VStack(alignment: .leading, spacing: 8) {
                ForEach(Array(modelWidoku.grupyLekcji.enumerated()), id: \.element.id) { indeks, grupa in
                    widokGrupyLekcji(grupa: grupa)

                    if indeks < modelWidoku.grupyLekcji.count - 1 {
                        Divider()
                    }
                }
            }
            .kartaAtomu()
        }
    }

    private var kartaInformacjiOBrakuZastępstw: some View {
        HStack(alignment: .center, spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.yellow)

            Text("Nie udało się pobrać danych o zastępstwach dla tego planu. Zalecane jest sprawdzenie ich przez tradycyjną stronę.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .kartaAtomu()
    }

    private var selektorDni: some View {
        Picker("Dzień tygodnia", selection: $wybranyDzień) {
            ForEach(Dzien.allCases) { dzień in
                Text(dzień.skróconyTytuł)
                    .tag(dzień)
            }
        }
        .pickerStyle(.segmented)
    }

    @ViewBuilder
    private var stopkaInformacjiPlanu: some View {
        Group {
            if modelWidoku.czyMaInformacjePlanu {
                DisclosureGroup(isExpanded: $czyRozwiniętoInformacjePlanu) {
                    VStack(alignment: .leading, spacing: 6) {
                        if let obowiazujeOd = modelWidoku.obowiazujeOd {
                            Text("Obowiązuje od **\(obowiazujeOd)**")
                        }

                        if let wygasa = modelWidoku.wygasa {
                            Text("Obowiązuje do **\(wygasa)**")
                        }

                        if let wygenerowano = modelWidoku.wygenerowano {
                            Text("Wygenerowano **\(wygenerowano)**")
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.top)
                } label: {
                    HStack(alignment: .center, spacing: 12) {
                        Image(systemName: "info.circle.text.page")
                            .font(.title2)

                        VStack(alignment: .leading, spacing: 2) {
                            Text("Dodatkowe informacje o planie lekcji")
                                .font(.footnote)

                            Text("Daty obowiązywania planu lekcji")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                .foregroundStyle(.primary)
                .font(.footnote)
                .kartaAtomu()
            }
        }
    }

    // MARK: - Budowanie widoków

    private func widokGrupyLekcji(grupa: GrupaLekcjiWidoku) -> some View {
        HStack(alignment: .center, spacing: 8) {
            Text("\(grupa.numer)")
                .font(.subheadline.weight(.semibold))
                .frame(width: 22)

            VStack(alignment: .leading, spacing: 8) {
                ForEach(grupa.lekcje) { lekcja in
                    KartaLekcji(
                        lekcja: lekcja,
                        czyPlanNauczyciela: czyPlanNauczyciela
                    )
                }
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 2) {
                Text(grupa.poczatek)
                    .font(.caption)
                    .foregroundStyle(.primary)
                    .monospacedDigit()

                Text(grupa.koniec)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .monospacedDigit()
            }
        }
    }
}

private struct KartaLekcji: View {
    let lekcja: LekcjaWidoku
    let czyPlanNauczyciela: Bool

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                if let opisZastępstwa = lekcja.opisZastępstwaDoWyświetlenia {
                    Text(
                        [lekcja.przedmiot, lekcja.tekstPomocniczy(czyPlanNauczyciela: czyPlanNauczyciela)]
                            .filter { !$0.isEmpty }
                            .joined(separator: " ")
                    )
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .strikethrough(true)

                    Text(opisZastępstwa)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundStyle(.primary)
                } else {
                    Text(lekcja.przedmiot)
                        .font(.subheadline.bold())

                    if !lekcja.tekstPomocniczy(czyPlanNauczyciela: czyPlanNauczyciela).isEmpty {
                        Text(lekcja.tekstPomocniczy(czyPlanNauczyciela: czyPlanNauczyciela))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }

            Spacer()
        }
        .padding(.vertical, 6)
        .padding(.horizontal, 8)
    }
}
