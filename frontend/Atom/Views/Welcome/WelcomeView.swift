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

struct WelcomeView: View {
    @Environment(AuthSessionViewModel.self) private var modelSesji

    @State private var czyPokazaćArkuszLogowania = false

    // MARK: - Widok

    var body: some View {
        NavigationStack {
            VStack {
                VStack(spacing: 16) {
                    Image("atom-icon")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 120, height: 120)

                    Text("Atom")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .fontDesign(.serif)

                    Text("Nowoczesna aplikacja stworzona z myślą o uczniach i nauczycielach.")
                        .font(.title3)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)

                Button {
                    czyPokazaćArkuszLogowania = true
                } label: {
                    Text("Rozpocznij")
                        .font(.headline)
                        .foregroundStyle(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background {
                            RoundedRectangle(cornerRadius: 20, style: .continuous)
                                .fill(Color.accentColor)
                                .overlay {
                                    LinearGradient(
                                        colors: [
                                            Color.white.opacity(0.25),
                                            Color.white.opacity(0.15),
                                            Color.clear
                                        ],
                                        startPoint: .top,
                                        endPoint: .bottom
                                    )
                                    .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                                }
                        }
                }
                .buttonStyle(.plain)
                .padding(.bottom)
                .sheet(isPresented: $czyPokazaćArkuszLogowania) {
                    VStack(spacing: 24) {
                        HStack(alignment: .lastTextBaseline) {
                            Text("Zaloguj się do aplikacji")
                                .font(.title3)
                                .fontWeight(.bold)

                            Text("Atom")
                                .font(.largeTitle)
                                .fontDesign(.serif)
                                .fontWeight(.bold)
                        }

                        AppleSignInButton()
                    }
                    .padding(24)
                    .presentationDetents([.fraction(0.3)])
                    .presentationDragIndicator(.hidden)
                }

                Link(destination: LinkiFunkcyjne.github) {
                    Text("Stworzone z ❤️ przez Kacpra Górkę")
                        .font(.footnote)
                        .fontDesign(.serif)
                }
                .foregroundStyle(.secondary)
            }
            .padding(.horizontal)
            .navigationTitle("Ekran początkowy")
            .toolbar(.hidden, for: .navigationBar)
            .disabled(modelSesji.czyŁaduje)
            .alert(
                "Wystąpił błąd",
                isPresented: Binding(
                    get: { modelSesji.błąd != nil },
                    set: { czyJestPrezentowany in
                        if !czyJestPrezentowany {
                            modelSesji.wyczyśćBłąd()
                        }
                    }
                )
            ) {
                Button("OK") {
                    modelSesji.wyczyśćBłąd()
                }
            } message: {
                Text(modelSesji.błąd ?? "")
            }
        }
    }
}
