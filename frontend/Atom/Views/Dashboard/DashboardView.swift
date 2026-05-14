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
import SwiftUI

struct DashboardView: View {
    @Binding var wybranaZakładka: AktualnaZakładka

    @State private var modelWidoku = DashboardViewModel()

    @Environment(\.colorScheme) private var schematKoloru
    @Environment(\.openURL) private var otwórzURL

    @State private var czyPokazaćZarządzanieKontem = false

    @AppStorage(KluczeUstawień.identyfikatorOddziału) private var identyfikatorOddziału: String = ""
    @AppStorage(KluczeUstawień.identyfikatorNauczyciela) private var identyfikatorNauczyciela: String = ""
    @AppStorage(KluczeUstawień.grupaZajęćLekcyjnych) private var grupaZajęćLekcyjnych: String = ""
    @AppStorage(KluczeUstawień.grupaZajęćPraktycznych) private var grupaZajęćPraktycznych: String = ""
    @AppStorage(KluczeUstawień.grupaWychowaniaFizycznego) private var grupaWychowaniaFizycznego: String = ""
    @AppStorage(KluczeUstawień.religia) private var religia = true
    @AppStorage(KluczeUstawień.edukacjaZdrowotna) private var edukacjaZdrowotna = true
    @AppStorage(KluczeUstawień.nazwa) private var nazwa: String = ""

    private let zegar = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    private var identyfikatorPlanu: String? {
        let identyfikator = !identyfikatorNauczyciela.isEmpty ? identyfikatorNauczyciela : identyfikatorOddziału
        return identyfikator.isEmpty ? nil : identyfikator
    }

    private var wybraneGrupy: [String]? {
        let grupy = [
            grupaZajęćLekcyjnych,
            grupaZajęćPraktycznych,
            grupaWychowaniaFizycznego
        ].filter { !$0.isEmpty }

        return grupy.isEmpty ? nil : grupy
    }

    private var kluczOdświeżaniaPlanu: [String] {
        [
            identyfikatorPlanu ?? "",
            modelWidoku.wybranyDzień.rawValue,
            grupaZajęćLekcyjnych,
            grupaZajęćPraktycznych,
            grupaWychowaniaFizycznego,
            religia.description,
            edukacjaZdrowotna.description
        ]
    }

    private var tekstPowitania: String {
        let przyciętaNazwa = nazwa.trimmingCharacters(in: .whitespacesAndNewlines)
        return przyciętaNazwa.isEmpty ? "Cześć Użytkowniku!" : "Cześć, \(przyciętaNazwa)!"
    }

    // MARK: - Widok

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                kartaSzczęśliwychNumerków
                if !modelWidoku.czyDaneZastępstwDostępne {
                    kartaInformacjiOBrakuZastępstw
                }
                kartaNadchodzącychZajęć

                if !identyfikatorNauczyciela.isEmpty {
                    kartaZasobówNauczyciela
                }

                kartaPlatformSzkolnych
                kartaMediówSpołecznościowych
            }
            .padding()
        }
        .refreshable {
            async let numerki: Void = modelWidoku.załadujNumerki(pomińCache: true)
            async let plan: Void = modelWidoku.załadujPlan(
                identyfikator: identyfikatorPlanu,
                grupy: wybraneGrupy,
                religia: religia,
                edukacjaZdrowotna: edukacjaZdrowotna,
                pomińCache: true
            )

            _ = await (numerki, plan)
        }
        .tłoAtomu(schematKoloru: schematKoloru)
        .navigationTitle("Strona główna")
        .navigationSubtitle(tekstPowitania)
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
        .task(id: modelWidoku.kluczDnia) {
            await modelWidoku.załadujNumerki()
        }
        .task(id: kluczOdświeżaniaPlanu) {
            await modelWidoku.załadujPlan(
                identyfikator: identyfikatorPlanu,
                grupy: wybraneGrupy,
                religia: religia,
                edukacjaZdrowotna: edukacjaZdrowotna
            )
        }
        .onReceive(zegar) { _ in
            modelWidoku.odświeżAktualnąDatę()
        }
    }

    // MARK: - Sekcje

    private var kartaSzczęśliwychNumerków: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: "numbersign")
                    .frame(width: 24, height: 24)
                    .foregroundStyle(.primary)

                Text("Szczęśliwe numerki")
                    .font(.headline)

                Spacer()

                if modelWidoku.czyŁadujeNumerki {
                    ProgressView()
                        .controlSize(.small)
                } else if let błąd = modelWidoku.tekstBłęduNumerków {
                    Text(błąd)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.trailing)
                } else {
                    Text(modelWidoku.opisNumerków)
                        .font(.subheadline)
                        .foregroundStyle(.primary)
                }
            }
        }
        .kartaAtomu()
    }

    private var kartaNadchodzącychZajęć: some View {
        Button {
            wybranaZakładka = .planLekcji
        } label: {
            VStack(alignment: .leading, spacing: 16) {
                HStack(spacing: 16) {
                    Image(systemName: "calendar.day.timeline.left")
                        .frame(width: 24, height: 24)
                        .foregroundStyle(.primary)

                    VStack(alignment: .leading, spacing: 2) {
                        Text("Nadchodzące zajęcia")
                            .font(.headline)
                            .foregroundStyle(.primary)

                        Text(modelWidoku.wybranyDzień.opis)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }

                if modelWidoku.czyŁadujePlan {
                    ProgressView()
                        .frame(maxWidth: .infinity)
                } else if let błąd = modelWidoku.tekstBłęduPlanu {
                    Text(błąd)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                } else if modelWidoku.czyPokazaćBrakLekcji {
                    Text(modelWidoku.komunikatPlanu)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                } else {
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(Array(modelWidoku.grupyLekcji.enumerated()), id: \.element.id) { indeks, grupa in
                            widokGrupyLekcji(grupa: grupa)
                            if indeks < modelWidoku.grupyLekcji.count - 1 {
                                Divider()
                            }
                        }
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .buttonStyle(.plain)
        .kartaAtomu()
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

    private var kartaZasobówNauczyciela: some View {
        VStack(alignment: .leading, spacing: 16) {
            nagłówekKarty(ikonaSystemowa: "person.text.rectangle", tytuł: "Zasoby nauczyciela")

            przyciskLinku(
                tytuł: "Poczta ZSE",
                opis: "Szkolna platforma poczty"
            ) {
                otwórzURL(LinkiFunkcyjne.poczta)
            } ikona: {
                Image(systemName: "mail.stack")
                    .frame(width: 16, height: 16)
                    .foregroundStyle(.primary)
            }

            Divider()

            przyciskLinku(
                tytuł: "Dziennik VULCAN",
                opis: "Szkolny dziennik elektroniczny"
            ) {
                otwórzURL(LinkiFunkcyjne.dziennik)
            } ikona: {
                Image(systemName: "document")
                    .frame(width: 16, height: 16)
                    .foregroundStyle(.primary)
            }
        }
        .kartaAtomu()
    }

    private var kartaPlatformSzkolnych: some View {
        VStack(alignment: .leading, spacing: 16) {
            nagłówekKarty(ikonaSystemowa: "server.rack", tytuł: "Platformy szkolne")

            przyciskLinku(
                tytuł: "Moodle",
                opis: "Szkolna platforma Moodle"
            ) {
                otwórzURL(LinkiFunkcyjne.moodle)
            } ikona: {
                Image("moodle-icon")
                    .renderingMode(.template)
                    .resizable()
                    .frame(width: 16, height: 16)
                    .foregroundStyle(.primary)
            }

            Divider()

            przyciskLinku(
                tytuł: "Rowerek",
                opis: "Szkolny projekt oparty na rywalizacji"
            ) {
                otwórzURL(LinkiFunkcyjne.rowerek)
            } ikona: {
                Image(systemName: "figure.indoor.cycle")
                    .frame(width: 16, height: 16)
                    .foregroundStyle(.primary)
            }
        }
        .kartaAtomu()
    }

    private var kartaMediówSpołecznościowych: some View {
        VStack(alignment: .leading, spacing: 16) {
            nagłówekKarty(ikonaSystemowa: "signature", tytuł: "Media społecznościowe")

            przyciskLinku(
                tytuł: "Facebook",
                opis: "@zse.elektronik"
            ) {
                otwórzLinkAplikacji(
                    aplikacja: "fb://profile",
                    stronaWWW: LinkiFunkcyjne.facebookZSE
                )
            } ikona: {
                Image("facebook-icon")
                    .renderingMode(.template)
                    .resizable()
                    .frame(width: 16, height: 16)
                    .foregroundStyle(.primary)
            }

            Divider()

            przyciskLinku(
                tytuł: "Instagram",
                opis: "@zse.bydgoszcz"
            ) {
                otwórzLinkAplikacji(
                    aplikacja: "instagram://user?username=zse.bydgoszcz",
                    stronaWWW: LinkiFunkcyjne.instagramZSE
                )
            } ikona: {
                Image("instagram-icon")
                    .renderingMode(.template)
                    .resizable()
                    .frame(width: 16, height: 16)
                    .foregroundStyle(.primary)
            }
        }
        .kartaAtomu()
    }

    // MARK: - Budowanie widoków

    private func widokGrupyLekcji(grupa: GrupaLekcjiWidoku) -> some View {
        let czyAktywna = modelWidoku.czyAktywna(grupa: grupa)

        return VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .center, spacing: 8) {
                Text("\(grupa.numer)")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.primary)
                    .frame(width: 22)

                VStack(alignment: .leading, spacing: 8) {
                    ForEach(grupa.lekcje) { lekcja in
                        widokLekcji(lekcja: lekcja)
                    }

                    if let pozostałyCzas = modelWidoku.opisPozostałegoCzasu(dla: grupa) {
                        Text("Zostało **\(pozostałyCzas)**")
                            .font(.caption2)
                            .foregroundStyle(.primary)
                            .padding(.horizontal, 20)
                            .padding(.vertical, 6)
                            .background {
                                Capsule()
                                    .foregroundStyle(.secondary)
                            }
                    } else if let czasDoRozpoczęcia = modelWidoku.opisCzasuDoRozpoczęcia(dla: grupa) {
                        Text("Zaczyna się za **\(czasDoRozpoczęcia)**")
                            .font(.caption2)
                            .foregroundStyle(.primary)
                            .padding(.horizontal, 20)
                            .padding(.vertical, 6)
                            .background {
                                Capsule()
                                    .foregroundStyle(.secondary)
                            }
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
        .padding(.vertical, czyAktywna ? 6 : 0)
        .offset(y: czyAktywna ? -4 : 0)
    }

    private func widokLekcji(lekcja: LekcjaWidoku) -> some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                if let opisZastępstwa = lekcja.opisZastępstwaDoWyświetlenia {
                    Text(
                        [lekcja.przedmiot, lekcja.tekstPomocniczyNaPulpicie]
                            .filter { !$0.isEmpty }
                            .joined(separator: " ")
                    )
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .strikethrough(true)

                    Text(opisZastępstwa)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundStyle(.primary)
                } else {
                    Text(lekcja.przedmiot)
                        .font(.subheadline.bold())

                    if !lekcja.tekstPomocniczyNaPulpicie.isEmpty {
                        Text(lekcja.tekstPomocniczyNaPulpicie)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }

            Spacer()
        }
        .padding(.vertical, 4)
        .padding(.horizontal, 8)
    }

    private func nagłówekKarty(ikonaSystemowa: String, tytuł: String) -> some View {
        HStack {
            Image(systemName: ikonaSystemowa)
                .frame(width: 24, height: 24)
                .foregroundStyle(.primary)

            Text(tytuł)
                .font(.headline)
        }
    }

    private func przyciskLinku<Ikona: View>(
        tytuł: String,
        opis: String,
        akcja: @escaping () -> Void,
        @ViewBuilder ikona: () -> Ikona
    ) -> some View {
        Button(action: akcja) {
            HStack(spacing: 12) {
                ikona()

                VStack(alignment: .leading, spacing: 2) {
                    Text(tytuł)
                        .font(.subheadline)

                    Text(opis)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundStyle(.secondary)
            }
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }

    // MARK: - Akcje

    private func otwórzLinkAplikacji(aplikacja: String, stronaWWW: URL) {
        if let urlAplikacji = URL(string: aplikacja), UIApplication.shared.canOpenURL(urlAplikacji) {
            otwórzURL(urlAplikacji)
            return
        }

        otwórzURL(stronaWWW)
    }
}
