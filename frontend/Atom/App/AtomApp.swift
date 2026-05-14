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
import UIKit

@main
struct AtomApp: App {

    // MARK: - Właściwości

    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @Environment(\.scenePhase) private var scenePhase
    @State private var modelSesji = AuthSessionViewModel()
    @State private var managerPowiadomień = PushNotificationsManager.współdzielony

    // MARK: - Widok

    var body: some Scene {
        WindowGroup {
            GłównyWidokAplikacji()
                .environment(modelSesji)
                .environment(managerPowiadomień)
                .task {
                    modelSesji.rozpocznijNasłuchiwanie()
                }
                .onChange(of: scenePhase) {
                    guard scenePhase == .active else {
                        return
                    }

                    modelSesji.zsynchronizujKontoAktualnejSesji()
                }
        }
    }
}

// MARK: - App Delegate

final class AppDelegate: NSObject, UIApplicationDelegate {
    
    // MARK: - Lifecycle

    func application(
        _ application: UIApplication,
        willFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        PushNotificationsManager.współdzielony.skonfiguruj()
        return true
    }

    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        Task { @MainActor in
            PushNotificationsManager.współdzielony.ustawTokenUrządzenia(deviceToken)
        }
    }
}

// MARK: - Główny widok aplikacji

private struct GłównyWidokAplikacji: View {
    @Environment(AuthSessionViewModel.self) private var modelSesji
    @Environment(PushNotificationsManager.self) private var managerPowiadomień

    @AppStorage(KluczeUstawień.czyKonfiguracjaZakończona) private var czyKonfiguracjaZakończona = false
    @AppStorage(KluczeUstawień.oddział) private var oddział: String = ""
    @AppStorage(KluczeUstawień.identyfikatorOddziału) private var identyfikatorOddziału: String = ""
    @AppStorage(KluczeUstawień.nauczyciel) private var nauczyciel: String = ""
    @AppStorage(KluczeUstawień.identyfikatorNauczyciela) private var identyfikatorNauczyciela: String = ""
    @AppStorage(KluczeUstawień.numerekUcznia) private var numerekUcznia: String = ""
    @AppStorage(KluczeUstawień.grupaZajęćLekcyjnych) private var grupaZajęćLekcyjnych: String = ""
    @AppStorage(KluczeUstawień.grupaZajęćPraktycznych) private var grupaZajęćPraktycznych: String = ""
    @AppStorage(KluczeUstawień.grupaWychowaniaFizycznego) private var grupaWychowaniaFizycznego: String = ""
    @AppStorage(KluczeUstawień.religia) private var religia = true
    @AppStorage(KluczeUstawień.edukacjaZdrowotna) private var edukacjaZdrowotna = true

    @State private var czyPokazaćKonfiguracjęJakoArkusz = false

    // MARK: - Właściwości obliczeniowe

    private var czyKonfiguracjaKompletna: Bool {
        !identyfikatorOddziału.isEmpty || !identyfikatorNauczyciela.isEmpty
    }

    private var podpisPreferencjiPowiadomień: String {
        [
            oddział,
            identyfikatorOddziału,
            nauczyciel,
            identyfikatorNauczyciela,
            numerekUcznia,
            grupaZajęćLekcyjnych,
            grupaZajęćPraktycznych,
            grupaWychowaniaFizycznego,
            religia.description,
            edukacjaZdrowotna.description
        ].joined(separator: "|")
    }

    // MARK: - Widok

    var body: some View {
        Group {
            if modelSesji.czyŁadowanieSesji {
                ZStack {
                    Color(.systemBackground)
                        .ignoresSafeArea()

                    ProgressView()
                        .controlSize(.regular)
                }
                .transition(.opacity)
            } else if !modelSesji.czyZalogowano {
                WelcomeView()
                    .transition(.opacity.combined(with: .scale(scale: 0.98)))
            } else if !czyKonfiguracjaZakończona {
                NavigationStack {
                    PersonalizationView()
                }
                .transition(.move(edge: .trailing).combined(with: .opacity))
            } else {
                MainTabView()
                    .onAppear {
                        czyPokazaćKonfiguracjęJakoArkusz = !czyKonfiguracjaKompletna
                    }
                    .sheet(isPresented: $czyPokazaćKonfiguracjęJakoArkusz) {
                        NavigationStack {
                            PersonalizationView(czyTrybKonfiguracji: true)
                                .navigationBarTitleDisplayMode(.inline)
                                .toolbar {
                                    ToolbarItem(placement: .navigationBarLeading) {
                                        Button("Zamknij") {
                                            czyPokazaćKonfiguracjęJakoArkusz = false
                                        }
                                        .disabled(!czyKonfiguracjaKompletna)
                                    }
                                }
                        }
                        .presentationDetents([.large])
                        .presentationDragIndicator(.visible)
                        .interactiveDismissDisabled(!czyKonfiguracjaKompletna)
                    }
                    .transition(.opacity)
            }
        }
        .animation(.smooth(duration: 0.35), value: modelSesji.czyŁadowanieSesji)
        .animation(.smooth(duration: 0.35), value: modelSesji.czyZalogowano)
        .animation(.smooth(duration: 0.35), value: czyKonfiguracjaZakończona)
        .onChange(of: podpisPreferencjiPowiadomień) {
            Task {
                await managerPowiadomień.zsynchronizujPreferencje()
            }
        }
    }
}
