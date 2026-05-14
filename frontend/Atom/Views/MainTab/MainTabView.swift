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

enum AktualnaZakładka: Hashable {
    case start
    case planLekcji
    case zastępstwa
    case ogłoszenia
    case więcej
}

struct MainTabView: View {
    @Environment(\.scenePhase) private var scenePhase
    @Environment(PushNotificationsManager.self) private var managerPowiadomień

    @State private var wybranaZakładka: AktualnaZakładka = .start
    @State private var wybranyDzieńPlanu: Dzien = .dzisiaj
    @State private var czyPokazaćInformacjeZastępstwZPowiadomienia = false

    // MARK: - Widok

    var body: some View {
        TabView(selection: $wybranaZakładka) {
            Tab(value: AktualnaZakładka.start) {
                NavigationStack {
                    DashboardView(wybranaZakładka: $wybranaZakładka)
                }
            } label: {
                Label("Start", systemImage: "text.rectangle.page")
                    .environment(\.symbolVariants, .none)
            }

            Tab(value: AktualnaZakładka.planLekcji) {
                NavigationStack {
                    TimetableView(wybranyDzień: $wybranyDzieńPlanu)
                }
            } label: {
                Label("Plan lekcji", systemImage: "chart.bar.horizontal.page")
            }

            Tab(value: AktualnaZakładka.zastępstwa) {
                NavigationStack {
                    SubstitutionsView(
                        czyPokazaćInformacjeZPowiadomienia: $czyPokazaćInformacjeZastępstwZPowiadomienia
                    )
                }
            } label: {
                Label("Zastępstwa", systemImage: "long.text.page.and.pencil")
            }

            Tab(value: AktualnaZakładka.ogłoszenia) {
                NavigationStack {
                    AnnouncementsView()
                }
            } label: {
                Label("Ogłoszenia", systemImage: "newspaper")
            }

            Tab(value: AktualnaZakładka.więcej) {
                NavigationStack {
                    MoreView(wybranaZakładka: $wybranaZakładka)
                }
            } label: {
                Label("Więcej", systemImage: "ellipsis")
            }
        }
        .onAppear {
            obsłużOczekiwaneMiejsceDocelowe()
            wyczyśćBadgeJeśliPotrzeba(dla: wybranaZakładka)
        }
        .onChange(of: wybranaZakładka) { _, nowaZakładka in
            wyczyśćBadgeJeśliPotrzeba(dla: nowaZakładka)
        }
        .onChange(of: managerPowiadomień.oczekiwaneMiejsceDocelowe) { _, _ in
            obsłużOczekiwaneMiejsceDocelowe()
        }
        .onChange(of: scenePhase) { _, nowaFaza in
            guard nowaFaza == .active else {
                return
            }

            wyczyśćBadgeJeśliPotrzeba(dla: wybranaZakładka)
        }
    }

    // MARK: - Powiadomienia

    private func obsłużOczekiwaneMiejsceDocelowe() {
        guard let miejsceDocelowe = managerPowiadomień.pobierzOczekiwaneMiejsceDocelowe() else {
            return
        }

        let zakładka = zakładka(dla: miejsceDocelowe.ekran)
        zastosujSzczegóły(miejscaDocelowego: miejsceDocelowe)
        wybranaZakładka = zakładka
        wyczyśćBadgeJeśliPotrzeba(dla: zakładka)
    }

    private func zakładka(dla ekran: DocelowyEkranPowiadomieniaPush) -> AktualnaZakładka {
        switch ekran {
        case .dashboard:
            return .start
        case .planLekcji:
            return .planLekcji
        case .zastępstwa:
            return .zastępstwa
        }
    }

    private func wyczyśćBadgeJeśliPotrzeba(dla zakładka: AktualnaZakładka) {
        switch zakładka {
        case .start, .planLekcji, .zastępstwa:
            managerPowiadomień.wyczyśćLokalnyBadge()
        case .ogłoszenia, .więcej:
            break
        }
    }

    private func zastosujSzczegóły(miejscaDocelowego miejsceDocelowe: MiejsceDocelowePowiadomieniaPush) {
        if let dzień = miejsceDocelowe.dzień {
            wybranyDzieńPlanu = dzień
        }

        if miejsceDocelowe.akcja == .pokażInformacjeDodatkowe {
            czyPokazaćInformacjeZastępstwZPowiadomienia = true
        }
    }
}
