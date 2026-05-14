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

struct AnnouncementsView: View {
    @Environment(\.colorScheme) private var schematKoloru
    @Environment(\.openURL) private var otwórzURL

    @State private var modelWidoku = AnnouncementsViewModel()

    @State private var czyPokazaćZarządzanieKontem = false

    // MARK: - Widok

    var body: some View {
        zawartość
        .tłoAtomu(schematKoloru: schematKoloru)
        .navigationTitle("Ogłoszenia")
        .navigationSubtitle("Aktualności")
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
            await modelWidoku.załadujPonownieJeśliPotrzeba()
        }
    }

    // MARK: - Sekcje

    @ViewBuilder
    private var zawartość: some View {
        if modelWidoku.czyŁaduje && modelWidoku.ogloszenia.isEmpty {
            wyśrodkowanaZawartość {
                ProgressView("Ładowanie ogłoszeń…")
            }
        } else if let błąd = modelWidoku.błąd, modelWidoku.ogloszenia.isEmpty {
            wyśrodkowanaZawartość {
                ContentUnavailableView(
                    "Nie udało się pobrać ogłoszeń",
                    systemImage: "exclamationmark.bubble.fill",
                    description: Text(błąd)
                )
            }
        } else if modelWidoku.ogloszenia.isEmpty {
            wyśrodkowanaZawartość {
                ContentUnavailableView(
                    "Nie udostępniono jeszcze żadnych ogłoszeń",
                    systemImage: "text.page.slash.fill"
                )
            }
        } else {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    ForEach(modelWidoku.ogloszenia) { ogloszenie in
                        przyciskOgloszenia(ogloszenie: ogloszenie)
                    }

                    sekcjaDoładowania
                }
                .padding()
            }
            .refreshable {
                await modelWidoku.odśwież(pomińCache: true)
            }
        }
    }

    // MARK: - Budowanie widoków

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
                await modelWidoku.odśwież(pomińCache: true)
            }
        }
    }

    @ViewBuilder
    private var sekcjaDoładowania: some View {
        if let błąd = modelWidoku.błąd, !modelWidoku.ogloszenia.isEmpty {
            Text(błąd)
                .font(.footnote)
                .foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(.top, 4)
        }

        if modelWidoku.czyMożnaZaładowaćWięcej {
            Button {
                Task {
                    await modelWidoku.załadujWięcej()
                }
            } label: {
                HStack(spacing: 10) {
                    if modelWidoku.czyŁadujeWięcej {
                        ProgressView()
                            .controlSize(.small)
                    } else {
                        Image(systemName: "text.append")
                    }

                    Text(modelWidoku.czyŁadujeWięcej ? "Ładowanie…" : "Pokaż starsze ogłoszenia")
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.plain)
            .kartaAtomu()
        }
    }

    // MARK: - Akcje

    private func przyciskOgloszenia(ogloszenie: OgloszenieWidoku) -> some View {
        Button {
            guard let url = URL(string: ogloszenie.ogloszenie.url) else {
                return
            }

            otwórzURL(url)
        } label: {
            VStack(alignment: .leading, spacing: 14) {
                if let url = ogloszenie.miniaturaURL {
                    AsyncImage(url: url) { faza in
                        switch faza {
                        case .empty:
                            ZStack {
                                RoundedRectangle(cornerRadius: 16, style: .continuous)
                                    .fill(.quaternary.opacity(0.4))

                                ProgressView()
                            }
                        case .success(let obraz):
                            obraz
                                .resizable()
                                .scaledToFill()
                        case .failure:
                            RoundedRectangle(cornerRadius: 16, style: .continuous)
                                .fill(.quaternary.opacity(0.4))
                                .overlay {
                                    Image(systemName: "photo")
                                        .foregroundStyle(.secondary)
                                }
                        @unknown default:
                            EmptyView()
                        }
                    }
                    .frame(height: 180)
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text(ogloszenie.tytul)
                        .font(.headline)
                        .multilineTextAlignment(.leading)

                    if !ogloszenie.stopka.isEmpty {
                        Text(ogloszenie.stopka)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                HStack {
                    Spacer()

                    Label("Otwórz artykuł", systemImage: "safari")
                        .font(.footnote.weight(.semibold))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .glassEffect()
                }
                .foregroundStyle(.primary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .buttonStyle(.plain)
        .kartaAtomu()
    }
}
