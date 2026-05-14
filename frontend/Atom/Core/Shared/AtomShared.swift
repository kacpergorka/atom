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

// MARK: - Linki funkcyjne

enum LinkiFunkcyjne {
    static let discord = URL(string: "https://discord.gg/5KjkvbGQWj")!
    static let dziennik = URL(string: "https://cufs.vulcan.net.pl/bydgoszcz/")!
    static let facebookKacper = URL(string: "https://www.facebook.com/whos.mountain")!
    static let facebookSamorząd = URL(string: "https://www.facebook.com/zse.samorzad")!
    static let facebookZSE = URL(string: "https://www.facebook.com/zse.elektronik")!
    static let github = URL(string: "https://github.com/kacpergorka/atom")!
    static let instagramKacper = URL(string: "https://www.instagram.com/whos.mountain")!
    static let instagramSamorząd = URL(string: "https://www.instagram.com/zse.samorzad")!
    static let instagramZSE = URL(string: "https://www.instagram.com/zse.bydgoszcz/")!
    static let moodle = URL(string: "https://moodle.zse.bydgoszcz.pl/login/index.php")!
    static let poczta = URL(string: "https://poczta.zse.bydgoszcz.pl")!
    static let rowerek = URL(string: "https://rowerek.zse.bydgoszcz.pl/")!
}

// MARK: - Linki statyczne

enum LinkiStatyczne {
    static let api = "https://api.kacpergorka.com"
    static let supabaseURL = "https://yzlrsckeejvfpghmugzb.supabase.co"
    static let supabaseAnonKey = "sb_publishable_kKYzB9GAesAN8tfULGgA5g_1Ppc6bbr"
}


// MARK: - Klucze ustawień

enum KluczeUstawień {
    static let czyKonfiguracjaZakończona = "czyKonfiguracjaZakończona"
    static let oddział = "oddział"
    static let identyfikatorOddziału = "identyfikatorOddziału"
    static let nauczyciel = "nauczyciel"
    static let identyfikatorNauczyciela = "identyfikatorNauczyciela"
    static let numerekUcznia = "numerekUcznia"
    static let nazwa = "nazwa"
    static let grupaZajęćLekcyjnych = "grupaZajęćLekcyjnych"
    static let grupaZajęćPraktycznych = "grupaZajęćPraktycznych"
    static let grupaWychowaniaFizycznego = "grupaWychowaniaFizycznego"
    static let religia = "religia"
    static let edukacjaZdrowotna = "edukacjaZdrowotna"
}

// MARK: - Podsumowanie konta

struct PodsumowanieKonta {
    let nazwa: String
    let oddział: String
    let identyfikatorOddziału: String
    let identyfikatorNauczyciela: String

    // MARK: - Właściwości obliczeniowe

    var czyNauczyciel: Bool {
        !identyfikatorNauczyciela.isEmpty
    }

    var opisRoli: String {
        if czyNauczyciel {
            return "Nauczyciel"
        }

        if !identyfikatorOddziału.isEmpty && !oddział.isEmpty {
            return "Uczeń (\(oddział))"
        }

        return "Nie skonfigurowano"
    }

    func nazwa(wartośćDomyślna: String) -> String {
        nazwa.isEmpty ? wartośćDomyślna : nazwa
    }
}

// MARK: - Grupa lekcji widoku

struct GrupaLekcjiWidoku: Identifiable, Equatable {
    let numer: Int
    let poczatek: String
    let koniec: String
    let lekcje: [LekcjaWidoku]

    // MARK: - Właściwości obliczeniowe

    var id: String {
        "\(numer)-\(poczatek)-\(koniec)"
    }

    // MARK: - Metody

    static func utwórz(z lekcje: [LekcjaWidoku]) -> [GrupaLekcjiWidoku] {
        Dictionary(grouping: lekcje) { "\($0.poczatek)-\($0.koniec)" }
            .compactMap { _, lekcjeWGupie in
                let posortowaneLekcje = lekcjeWGupie.sorted { $0.numer < $1.numer }

                guard let pierwszaLekcja = posortowaneLekcje.first else {
                    return nil
                }

                return GrupaLekcjiWidoku(
                    numer: pierwszaLekcja.numer,
                    poczatek: pierwszaLekcja.poczatek,
                    koniec: pierwszaLekcja.koniec,
                    lekcje: posortowaneLekcje
                )
            }
            .sorted { $0.numer < $1.numer }
    }
}

// MARK: - Rozszerzenie lekcji widoku

extension LekcjaWidoku {

    // MARK: - Właściwości obliczeniowe

    var opisZastępstwaDoWyświetlenia: String? {
        zastepstwo?.isEmpty == false ? zastepstwo : nil
    }

    // MARK: - Metody

    func tekstPomocniczy(czyPlanNauczyciela: Bool) -> String {
        let głównyOpis = czyPlanNauczyciela ? oddzialy : nauczyciel
        return zbudujTekstPomocniczy(głównyOpis: głównyOpis)
    }

    var tekstPomocniczyNaPulpicie: String {
        let głównyOpis = !nauczyciel.isEmpty ? nauczyciel : oddzialy
        return zbudujTekstPomocniczy(głównyOpis: głównyOpis)
    }

    private func zbudujTekstPomocniczy(głównyOpis: String) -> String {
        if głównyOpis.isEmpty {
            return sala
        }

        if sala.isEmpty {
            return głównyOpis
        }

        return "\(głównyOpis) (\(sala))"
    }
}

// MARK: - Rozszerzenie widoku

extension View {

    // MARK: - Style widoków

    func tłoAtomu(schematKoloru: ColorScheme) -> some View {
        background(schematKoloru == .light ? Color(.secondarySystemBackground) : Color.clear)
    }

    func kartaAtomu() -> some View {
        padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .glassEffect(.clear, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    // MARK: - Arkusze

    func arkuszZarządzaniaKontem(czyPokazać: Binding<Bool>) -> some View {
        sheet(isPresented: czyPokazać) {
            AccountManagementView()
                .presentationDetents([.fraction(0.3)])
                .presentationDragIndicator(.hidden)
        }
    }
}
