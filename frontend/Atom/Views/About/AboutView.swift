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

struct AboutView: View {
    private struct LinkSpołecznościowy: Identifiable {
        let id = UUID()
        let nazwa: String
        let opis: String
        let ikona: String
        let adres: URL
    }

    private let linkiAutora = [
        LinkSpołecznościowy(
            nazwa: "Instagram",
            opis: "@whos.mountain",
            ikona: "instagram-icon",
            adres: LinkiFunkcyjne.instagramKacper
        ),
        LinkSpołecznościowy(
            nazwa: "Facebook",
            opis: "@whos.mountain",
            ikona: "facebook-icon",
            adres: LinkiFunkcyjne.facebookKacper
        )
    ]

    private let linkiSamorządu = [
        LinkSpołecznościowy(
            nazwa: "Instagram",
            opis: "@zse.samorzad",
            ikona: "instagram-icon",
            adres: LinkiFunkcyjne.instagramSamorząd
        ),
        LinkSpołecznościowy(
            nazwa: "Facebook",
            opis: "@zse.samorzad",
            ikona: "facebook-icon",
            adres: LinkiFunkcyjne.facebookSamorząd
        )
    ]

    private let linkiProjektu = [
        LinkSpołecznościowy(
            nazwa: "GitHub",
            opis: "kacpergorka/atom",
            ikona: "github-icon",
            adres: LinkiFunkcyjne.github
        )
    ]

    private var wersjaAplikacji: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "0.0.0"
    }

    // MARK: - Widok

    var body: some View {
        Form {
            Section {
                HStack(alignment: .center, spacing: 12) {
                    Image("atom-icon")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 75, height: 75)

                    VStack(alignment: .leading, spacing: 2) {
                        Text("Atom")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .fontDesign(.serif)

                        Text("Wersja \(wersjaAplikacji)")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .center)
                .listRowInsets(EdgeInsets())
                .listRowBackground(Color.clear)
            }

            sekcjaLinków(linki: linkiAutora)
            sekcjaLinków(linki: linkiSamorządu)
            sekcjaLinków(linki: linkiProjektu)
        }
        .scrollDisabled(true)
        .navigationTitle("O aplikacji")
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Budowanie widoków

    private func sekcjaLinków(linki: [LinkSpołecznościowy]) -> some View {
        Section {
            ForEach(linki) { link in
                Link(destination: link.adres) {
                    HStack(spacing: 12) {
                        Image(link.ikona)
                            .renderingMode(.template)
                            .resizable()
                            .frame(width: 20, height: 20)
                            .foregroundStyle(.primary)

                        VStack(alignment: .leading, spacing: 2) {
                            Text(link.nazwa)
                            Text(link.opis)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }

                        Spacer()

                        Image(systemName: "chevron.right")
                            .foregroundStyle(.tertiary)
                    }
                }
                .foregroundStyle(.primary)
            }
        }
    }
}
