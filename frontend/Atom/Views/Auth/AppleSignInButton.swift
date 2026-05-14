//
//     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄
//    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███
//    ████       ██     ██    ██  ████████
//   ██  ██      ██     ██    ██  ██ ██ ██
//   ██████      ██     ██    ██  ██ ▀▀ ██
//  ▄██  ██▄     ██      ██▄▄██   ██    ██
//  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀
//

import AuthenticationServices
import CryptoKit
import Security
import SwiftUI

struct AppleSignInButton: View {
    @Environment(AuthSessionViewModel.self) private var modelSesji

    @State private var aktualnyNonce: String?

    var poZalogowaniu: (() -> Void)?

    // MARK: - Widok

    var body: some View {
        SignInWithAppleButton(.continue) { żądanie in
            let nonce = losowyNonce()
            aktualnyNonce = nonce
            żądanie.requestedScopes = [.email, .fullName]
            żądanie.nonce = sha256(nonce)
        } onCompletion: { wynik in
            obsłużLogowanieApple(wynik)
        }
        .frame(height: 50)
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    // MARK: - Akcje

    private func obsłużLogowanieApple(_ wynik: Result<ASAuthorization, Error>) {
        switch wynik {
        case .success(let autoryzacja):
            guard
                let credential = autoryzacja.credential as? ASAuthorizationAppleIDCredential,
                let tokenDanych = credential.identityToken,
                let idToken = String(data: tokenDanych, encoding: .utf8),
                let nonce = aktualnyNonce
            else {
                modelSesji.ustawBłąd("Nie udało się odczytać danych logowania Apple.")
                return
            }

            Task {
                await modelSesji.zalogujZApple(
                    idToken: idToken,
                    nonce: nonce,
                    nazwa: nazwaZApple(credential.fullName)
                )

                if modelSesji.czyZalogowano {
                    poZalogowaniu?()
                }
            }

        case .failure(let błąd):
            if let błądAutoryzacji = błąd as? ASAuthorizationError,
               błądAutoryzacji.code == .canceled {
                return
            }

            modelSesji.ustawBłąd(błąd.komunikatDlaUżytkownika)
        }
    }

    // MARK: - Prywatne metody

    private func nazwaZApple(_ pełnaNazwa: PersonNameComponents?) -> String? {
        guard let pełnaNazwa else {
            return nil
        }

        let imię = pełnaNazwa.givenName?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let nazwisko = pełnaNazwa.familyName?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let pełna = [imię, nazwisko].filter { !$0.isEmpty }.joined(separator: " ")

        if !pełna.isEmpty {
            return pełna
        }

        let sformatowana = PersonNameComponentsFormatter()
            .string(from: pełnaNazwa)
            .trimmingCharacters(in: .whitespacesAndNewlines)

        return sformatowana.isEmpty ? nil : sformatowana
    }

    private func losowyNonce(długość: Int = 32) -> String {
        precondition(długość > 0)

        let znaki = Array("0123456789ABCDEFGHIJKLMNOPQRSTUVXYZabcdefghijklmnopqrstuvwxyz-._")
        var wynik = ""
        var pozostałaDługość = długość

        while pozostałaDługość > 0 {
            var losowaWartość: UInt8 = 0
            let status = SecRandomCopyBytes(kSecRandomDefault, 1, &losowaWartość)
            precondition(status == errSecSuccess, "Nie udało się wygenerować bezpiecznego nonce.")

            if Int(losowaWartość) < znaki.count {
                wynik.append(znaki[Int(losowaWartość)])
                pozostałaDługość -= 1
            }
        }

        return wynik
    }

    private func sha256(_ wejście: String) -> String {
        let dane = Data(wejście.utf8)
        let skrót = SHA256.hash(data: dane)
        return skrót.map { String(format: "%02x", $0) }.joined()
    }
}
