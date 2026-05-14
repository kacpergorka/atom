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

struct SubstitutionsView: View {
    private enum WidokAkcji: String, CaseIterable, Identifiable {
        case informacje = "Informacje dodatkowe"
        case zastępstwa = "Wszystkie zastępstwa"

        var id: String {
            rawValue
        }
    }

    @Environment(\.colorScheme) private var schematKoloru

    @State private var modelWidoku = SubstitutionsViewModel()

    @State private var wybranaAkcja: WidokAkcji = .zastępstwa
    @State private var czyPokazaćInformacje = false
    @State private var czyPokazaćZarządzanieKontem = false
    @Binding private var czyPokazaćInformacjeZPowiadomienia: Bool

    init(czyPokazaćInformacjeZPowiadomienia: Binding<Bool>) {
        self._czyPokazaćInformacjeZPowiadomienia = czyPokazaćInformacjeZPowiadomienia
    }

    private func odśwież() async {
        await modelWidoku.załaduj(pomińCache: true)
    }

    // MARK: - Widok

    var body: some View {
        zawartość
            .tłoAtomu(schematKoloru: schematKoloru)
            .navigationTitle("Zastępstwa")
            .navigationSubtitle(modelWidoku.dni.isEmpty ? "Dni tygodnia" : modelWidoku.dni)
            .toolbarTitleDisplayMode(.inlineLarge)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        czyPokazaćZarządzanieKontem = true
                    } label: {
                        Image(systemName: "person.crop.circle")
                            .font(.title2)
                    }
                }
            }
            .arkuszZarządzaniaKontem(czyPokazać: $czyPokazaćZarządzanieKontem)
            .task {
                await modelWidoku.załaduj()
            }
            .onAppear {
                obsłużInformacjeZPowiadomienia()
            }
            .onChange(of: czyPokazaćInformacjeZPowiadomienia) { _, _ in
                obsłużInformacjeZPowiadomienia()
            }
            .sheet(isPresented: $czyPokazaćInformacje) {
                arkuszInformacji
            }
    }

    // MARK: - Sekcje

    @ViewBuilder
    private var zawartość: some View {
        if modelWidoku.czyŁaduje && modelWidoku.zastępstwa == nil {
            wyśrodkowanaZawartość {
                ProgressView("Ładowanie zastępstw…")
            }
        } else if let błąd = modelWidoku.błąd {
            wyśrodkowanaZawartość {
                ContentUnavailableView(
                    "Nie udało się pobrać zastępstw",
                    systemImage: "exclamationmark.bubble.fill",
                    description: Text(błąd)
                )
            }
        } else if modelWidoku.zastępstwa != nil {
            if modelWidoku.grupyZastępstw.isEmpty {
                GeometryReader { geometria in
                    ScrollView {
                        VStack(alignment: .leading, spacing: 12) {
                            selektorSekcji

                            ContentUnavailableView {
                                Label("Brak opublikowanych wpisów zastępstw.", systemImage: "text.page.slash.fill")
                            } description: {
                                Text("Sprawdź informacje dodatkowe, aby dowiedzieć się więcej.")
                            }
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
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
                        selektorSekcji

                        VStack(spacing: 12) {
                            ForEach(modelWidoku.grupyZastępstw) { grupa in
                                kartaNauczyciela(grupa: grupa)
                            }
                        }
                    }
                    .padding()
                }
                .refreshable {
                    await odśwież()
                }
            }
        } else {
            wyśrodkowanaZawartość {}
        }
    }

    private func wyśrodkowanaZawartość<Content: View>(
        @ViewBuilder content: @escaping () -> Content
    ) -> some View {
        GeometryReader { geometria in
            ScrollView {
                content()
                    .frame(maxWidth: .infinity)
                    .frame(minHeight: geometria.size.height)
            }
            .refreshable {
                await odśwież()
            }
        }
    }

    private func obsłużInformacjeZPowiadomienia() {
        guard czyPokazaćInformacjeZPowiadomienia else {
            return
        }

        czyPokazaćInformacje = true
        czyPokazaćInformacjeZPowiadomienia = false
    }

    private var selektorSekcji: some View {
        Picker("Sekcja", selection: $wybranaAkcja) {
            ForEach(WidokAkcji.allCases) { akcja in
                Text(akcja.rawValue)
                    .tag(akcja)
            }
        }
        .pickerStyle(.segmented)
        .onChange(of: wybranaAkcja) { _, nowaWartość in
            guard nowaWartość == .informacje else {
                return
            }

            czyPokazaćInformacje = true
            wybranaAkcja = .zastępstwa
        }
    }

    private var arkuszInformacji: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 8) {
                    ForEach(modelWidoku.informacjeDodatkowe) { informacja in
                        if informacja.czyPusta {
                            Spacer()
                                .frame(height: 8)
                        } else {
                            Text(informacja.tekst)
                        }
                    }
                }
                .padding()
                .font(.headline)
                .fontWeight(.medium)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .navigationTitle("Informacje dodatkowe")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button {
                        czyPokazaćInformacje = false
                    } label: {
                        Image(systemName: "xmark")
                    }
                    .accessibilityLabel("Zamknij")
                }
            }
        }
        .presentationDetents([.fraction(0.8), .large])
        .presentationContentInteraction(.resizes)
        .presentationDragIndicator(.visible)
    }

    // MARK: - Budowanie widoków

    private func kartaNauczyciela(grupa: GrupaZastępstwWidoku) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 2) {
                Text(grupa.nauczyciel)
                    .font(.headline)
                    .fontWeight(.bold)

                Text(grupa.dzień.map { "Nauczyciel (\($0))" } ?? "Nauczyciel")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            ForEach(Array(grupa.zastępstwa.enumerated()), id: \.offset) { indeks, zastępstwo in
                if indeks > 0 {
                    Divider()
                }

                WierszZastępstwa(zastępstwo: zastępstwo)
            }
        }
        .kartaAtomu()
    }
}

private struct WierszZastępstwa: View {
    let zastępstwo: Zastepstwo

    var body: some View {
        HStack(alignment: .center, spacing: 16) {
            Text(zastępstwo.lekcja.map(String.init) ?? "-")
                .font(.subheadline.weight(.semibold))
                .frame(width: 22)

            VStack(alignment: .leading, spacing: 4) {
                Text(zastępstwo.tresc?.isEmpty == false ? zastępstwo.tresc ?? "" : "Brak")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundStyle(.primary)

                if let stopka = zastępstwo.stopka, !stopka.isEmpty {
                    Text(stopka)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                } else {
                    Text("Brak dodatkowych informacji")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
    }
}
