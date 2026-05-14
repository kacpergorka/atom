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

struct AccountManagementView: View {
    @Environment(\.dismiss) private var zamknijWidok
    @Environment(AuthSessionViewModel.self) private var modelSesji

    @AppStorage(KluczeUstawień.nazwa) private var nazwa: String = ""
    @AppStorage(KluczeUstawień.oddział) private var oddział: String = ""
    @AppStorage(KluczeUstawień.identyfikatorOddziału) private var identyfikatorOddziału: String = ""
    @AppStorage(KluczeUstawień.identyfikatorNauczyciela) private var identyfikatorNauczyciela: String = ""

    @State private var czyPokazaćPełnoekranowąKonfigurację = false
    @State private var czyPokazaćPotwierdzenieWylogowania = false

    private var podsumowanieKonta: PodsumowanieKonta {
        PodsumowanieKonta(
            nazwa: nazwa,
            oddział: oddział,
            identyfikatorOddziału: identyfikatorOddziału,
            identyfikatorNauczyciela: identyfikatorNauczyciela
        )
    }

    private var czyMożnaZamknąćKonfigurację: Bool {
        !identyfikatorOddziału.isEmpty || !identyfikatorNauczyciela.isEmpty
    }

    private var powiązanieBłędu: Binding<Bool> {
        Binding(
            get: {
                modelSesji.błąd != nil
            },
            set: { czyJestPrezentowany in
                if !czyJestPrezentowany {
                    modelSesji.wyczyśćBłąd()
                }
            }
        )
    }

    // MARK: - Widok

    var body: some View {
        NavigationStack {
            Form {
                HStack(spacing: 8) {
                    Image(systemName: "person.crop.circle")
                        .font(.largeTitle)

                    VStack(alignment: .leading) {
                        Text(podsumowanieKonta.nazwa(wartośćDomyślna: "Brak danych"))
                            .font(.headline)
                            .fontDesign(.serif)

                        Text(podsumowanieKonta.opisRoli)
                            .foregroundStyle(.secondary)
                            .font(.footnote)
                    }

                    Spacer()

                    Button {
                        czyPokazaćPełnoekranowąKonfigurację = true
                    } label: {
                        Image(systemName: "slider.horizontal.3")
                            .font(.title3)
                            .frame(height: 30)
                    }
                    .buttonStyle(.glass)
                    .foregroundStyle(.primary)

                    Button(role: .destructive) {
                        czyPokazaćPotwierdzenieWylogowania = true
                    } label: {
                        Image(systemName: "rectangle.portrait.and.arrow.right.fill")
                            .font(.title3)
                            .frame(height: 30)
                    }
                    .buttonStyle(.glass)
                    .foregroundStyle(.red)
                    .alert("Wylogować się?", isPresented: $czyPokazaćPotwierdzenieWylogowania) {
                        Button("Anuluj", role: .cancel) {
                        }
                        Button("Wyloguj", role: .destructive) {
                            Task {
                                await modelSesji.wyloguj()
                            }
                        }
                    } message: {
                        Text("Czy na pewno chcesz wylogować się ze swojego konta?")
                    }
                }
            }
            .disabled(modelSesji.czyŁaduje)
            .alert(
                "Wystąpił błąd",
                isPresented: powiązanieBłędu
            ) {
                Button("OK") {
                    modelSesji.wyczyśćBłąd()
                }
            } message: {
                Text(modelSesji.błąd ?? "")
            }
            .navigationTitle("Zarządzanie kontem")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(role: .close) {
                        zamknijWidok()
                    }
                }
            }
            .fullScreenCover(isPresented: $czyPokazaćPełnoekranowąKonfigurację) {
                NavigationStack {
                    PersonalizationView(czyTrybKonfiguracji: true)
                        .toolbar {
                            ToolbarItem(placement: .cancellationAction) {
                                Button(role: .close) {
                                    czyPokazaćPełnoekranowąKonfigurację = false
                                }
                                .disabled(!czyMożnaZamknąćKonfigurację)
                            }
                        }
                }
            }
        }
    }
}
