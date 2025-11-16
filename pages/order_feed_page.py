from pages.base_page import BasePage
from locators.locators import OrderFeedLocators
import allure


class OrderFeedPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step('Проверить загрузку страницы ленты заказов')
    def is_order_feed_page_loaded(self):
        return self.is_element_visible(OrderFeedLocators.title_orders_list)

    @allure.step('Получить значение счетчика "Выполнено за все время"')
    def get_total_orders_count(self):
        try:
            counter = self.find_element(OrderFeedLocators.total_orders_counter)
            return int(counter.text) if counter.text else 0
        except Exception:
            return 0

    @allure.step('Получить значение счетчика "Выполнено за сегодня"')
    def get_today_orders_count(self):
        try:
            counter = self.find_element(OrderFeedLocators.dayly_orders_counter)
            return int(counter.text) if counter.text else 0
        except Exception:
            return 0

    @allure.step('Получить список номеров заказов в разделе "В работе"')
    def get_orders_in_progress(self):
        try:
            orders_elements = self.find_elements(OrderFeedLocators.number_order_in_job)
            return [order.text for order in orders_elements if order.text]
        except Exception:
            return []

    @allure.step('Получить нормализованный список номеров заказов в разделе "В работе"')
    def get_orders_in_progress_normalized(self):
        try:
            orders_elements = self.find_elements(OrderFeedLocators.number_order_in_job)
            normalized_orders = []
            for order in orders_elements:
                if order.text:
                    # Убираем ведущие нули и преобразуем в число
                    normalized_orders.append(str(int(order.text)))
            return normalized_orders
        except Exception:
            return []

    @allure.step('Нормализовать номер заказа')
    def normalize_order_number(self, order_number):
        if isinstance(order_number, str):
            # Убираем ведущие нули
            return str(int(order_number))
        else:
            return str(order_number)

    @allure.step('Ждать обновления счетчиков')
    def wait_for_counters_update(self, initial_total, initial_today, timeout=7, poll_interval=0.3):
        """
        Ждём, пока увеличится нужный счётчик(и).

        Логика:
        - если initial_total > 0 и initial_today == 0  → следим только за total
        - если initial_today > 0 и initial_total == 0  → следим только за today
        - если оба > 0                                → достаточно роста любого
        """

        def condition():
            current_total = self.get_total_orders_count()
            current_today = self.get_today_orders_count()

            cond_total = current_total > initial_total if initial_total else False
            cond_today = current_today > initial_today if initial_today else False

            # Следим только за total
            if initial_total and not initial_today:
                return cond_total

            # Следим только за today
            if initial_today and not initial_total:
                return cond_today

            # Следим за обоими (достаточно роста любого)
            if initial_total and initial_today:
                return cond_total or cond_today

            # На случай, если вдруг оба 0 — fallback
            return current_total > initial_total or current_today > initial_today

        return self.wait_until(condition, timeout=timeout, poll_frequency=poll_interval)

    @allure.step('Ждать появления заказа в разделе "В работе"')
    def wait_for_order_in_progress(self, order_number, timeout=10, poll_interval=0.5):
        """Ждём, пока номер заказа появится в списке 'В работе'."""
        normalized_order = self.normalize_order_number(order_number)

        def condition():
            orders_in_progress = self.get_orders_in_progress_normalized()
            return normalized_order in orders_in_progress

        return self.wait_until(condition, timeout=timeout, poll_frequency=poll_interval)
