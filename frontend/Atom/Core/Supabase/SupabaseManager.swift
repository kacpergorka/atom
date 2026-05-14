//
//     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄
//    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███
//    ████       ██     ██    ██  ████████
//   ██  ██      ██     ██    ██  ██ ██ ██
//   ██████      ██     ██    ██  ██ ▀▀ ██
//  ▄██  ██▄     ██      ██▄▄██   ██    ██
//  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀
//

import Foundation
import Supabase

enum SupabaseManager {
    // MARK: - Właściwości

    static let współdzielony: SupabaseClient? = {
        guard
            let adresURL = URL(string: LinkiStatyczne.supabaseURL),
            !LinkiStatyczne.supabaseURL.isEmpty,
            !LinkiStatyczne.supabaseAnonKey.isEmpty
        else {
            return nil
        }

        return SupabaseClient(
            supabaseURL: adresURL,
            supabaseKey: LinkiStatyczne.supabaseAnonKey
        )
    }()
}
