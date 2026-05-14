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

struct MoreView: View {
    @Environment(\.openURL) private var otwórzURL
    @Environment(AuthSessionViewModel.self) private var modelSesji

    @Binding var wybranaZakładka: AktualnaZakładka

    @AppStorage(KluczeUstawień.nazwa) private var nazwa: String = ""
    @AppStorage(KluczeUstawień.oddział) private var oddział: String = ""
    @AppStorage(KluczeUstawień.identyfikatorOddziału) private var identyfikatorOddziału: String = ""
    @AppStorage(KluczeUstawień.identyfikatorNauczyciela) private var identyfikatorNauczyciela: String = ""

    private var podsumowanieKonta: PodsumowanieKonta {
        PodsumowanieKonta(
            nazwa: nazwa,
            oddział: oddział,
            identyfikatorOddziału: identyfikatorOddziału,
            identyfikatorNauczyciela: identyfikatorNauczyciela
        )
    }

    @State private var czyPokazaćPełnoekranowąKonfigurację = false
    @State private var czyPokazaćPotwierdzenieWylogowania = false
    @State private var czyPokazaćZarządzanieKontem = false
    private var czyMożnaZamknąćKonfigurację: Bool {
        !identyfikatorOddziału.isEmpty || !identyfikatorNauczyciela.isEmpty
    }

    // MARK: - Widok

    var body: some View {
        Form {
            Section {
                HStack(spacing: 8) {
                    Image(systemName: "person.text.rectangle.fill")
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
                    .alert("Jesteś pewien?", isPresented: $czyPokazaćPotwierdzenieWylogowania) {
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

            Section {
                przyciskZakładki(tytuł: "Start", ikona: "text.rectangle.page", zakładka: .start)
                przyciskZakładki(tytuł: "Plan lekcji", ikona: "chart.bar.horizontal.page.fill", zakładka: .planLekcji)
                przyciskZakładki(tytuł: "Zastępstwa", ikona: "long.text.page.and.pencil.fill", zakładka: .zastępstwa)
                przyciskZakładki(tytuł: "Ogłoszenia", ikona: "newspaper.fill", zakładka: .ogłoszenia)
            }

            Section {
                NavigationLink {
                    AboutView()
                } label: {
                    Label("O aplikacji", systemImage: "info.circle.text.page.fill")
                }
            }


            Section(
                footer: Text("Dołącz do serwera Discord i pomóż rozwijać aplikację.")
            ) {
                Button {
                    otwórzURL(LinkiFunkcyjne.discord)
                } label: {
                    Label {
                        Text("Znalazłeś/aś błąd?")
                    } icon: {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundStyle(.yellow)
                    }
                }
            }
        }
        .tint(.primary)
        .navigationTitle("Więcej")
        .navigationSubtitle("Dodatkowe informacje")
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

    // MARK: - Budowanie widoków

    private func przyciskZakładki(tytuł: String, ikona: String, zakładka: AktualnaZakładka) -> some View {
        Button {
            wybranaZakładka = zakładka
        } label: {
            Label(tytuł, systemImage: ikona)
        }
    }
}
