# Azure Reservation Exchange Resources

## Knowledge

- [Microsoft: Self-service exchanges and refunds for Azure Reservations](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/exchange-and-refund-azure-reservations)
  Fonte principale per meccanica refund più purchase, commitment residuo, limiti e trattamento per contratto.
- [Microsoft: Buy an Azure reservation](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/prepare-buy-reservation)
  Usare per pagamento upfront o mensile, frequenza nei dati e vincoli dell'exchange.
- [Microsoft: View reservation purchase and refund transactions](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/view-purchase-refunds)
  Usare per individuare e scaricare le due gambe dell'exchange.
- [Microsoft: View amortized benefit costs](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/view-amortized-costs)
  Usare per distinguere costo actual, costo amortized e quota inutilizzata.
- [Microsoft: EA usage, refund and invoice reconciliation](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/direct-ea-azure-usage-charges-invoices#understand-refunded-overage-credits)
  Usare per separare Azure Prepayment, overage, adjustment e credit note.
- [Microsoft: Reservation Transactions REST API](https://learn.microsoft.com/en-us/rest/api/consumption/reservation-transactions/list?view=rest-consumption-2024-08-01)
  Usare per automazione, campi evento e insidia tra `EventDate` e `BillingMonth`.
- [Dossier locale: trattamento finanziario completo](tmp/.research/2026-07-27-azure-reservation-exchange-financial-treatment.md)
  Ricerca di supporto aggiornata al 27 luglio 2026, con fatti, inferenze e gap separati.

## Wisdom (Communities)

- [FinOps Foundation Community](https://www.finops.org/community/)
  Comunità professionale per confrontare pratiche di chargeback, riconciliazione e collaborazione tra Engineering e Finance.

## Gaps

- Il cambio applicato alla gamba refund MCA non è chiarito dalla documentazione generale.
- Il trattamento fiscale puntuale richiede invoice, credit note e regole della giurisdizione.
- L'applicazione del minore tra prezzo storico e corrente alla gamba refund di un exchange va verificata sul quote reale.
