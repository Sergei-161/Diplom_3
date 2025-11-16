from pages.base_page import BasePage
from locators.locators import MainPageLocators
from data.urls import MainUrl
import allure


class MainPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.url = MainUrl.MAIN_URL

    @allure.step('Открыть главную страницу')
    def open(self):
        self.driver.get(self.url)
        self.wait_for_page_load()

    # ===== Навигация в хедере =====

    @allure.step('Кликнуть по кнопке "Конструктор"')
    def click_constructor(self):
        self.click_button(MainPageLocators.constructor_button)

    @allure.step('Кликнуть по кнопке "Лента заказов"')
    def click_order_feed(self):
        self.click_button(MainPageLocators.order_feed_button)

    # ===== Модалка ингредиента =====

    @allure.step('Кликнуть по ингредиенту')
    def click_ingredient(self):
        self.click_button(MainPageLocators.fluorescent_bun)

    @allure.step('Проверить видимость модального окна ингредиента')
    def is_ingredient_modal_visible(self):
        return self.is_element_visible(MainPageLocators.ingredient_modal)

    @allure.step('Проверить, что модальное окно ингредиента закрыто')
    def is_ingredient_modal_closed(self):
        return self.is_element_not_visible(MainPageLocators.ingredient_modal)

    @allure.step('Закрыть модальное окно ингредиента по крестику/оверлею')
    def close_ingredient_modal(self):
        try:
            # сначала пробуем крестик
            self.click_button(MainPageLocators.close_ingredient_modal)
        except Exception:
            # если не получилось, пробуем клик по оверлею
            try:
                if self.is_element_visible(MainPageLocators.modal_overlay, timeout=2):
                    self.click_button(MainPageLocators.modal_overlay)
            except Exception:
                # последний шанс — принудительное закрытие
                self.force_close_modals()

    # ===== Работа с ингредиентом и счётчиком =====

    @allure.step('Перетащить ингредиент в конструктор')
    def drag_ingredient_to_constructor(self):
        # на всякий случай закрываем все модалки
        self.close_all_modals()

        # ждём появления элементов
        self.wait_element_visible(MainPageLocators.fluorescent_bun)
        self.wait_element_visible(MainPageLocators.constructor_drop_area)

        # запоминаем текущий счётчик
        initial = self.get_ingredient_counter()

        # перетаскиваем ингредиент
        self.drag_and_drop(
            MainPageLocators.fluorescent_bun,
            MainPageLocators.constructor_drop_area,
        )

        # ждём, пока счётчик увеличится (если не увеличился — тест упадёт по assert)
        self.wait_until(
            lambda: self.get_ingredient_counter() > initial,
            timeout=5,
            poll_frequency=0.5,
        )

    @allure.step('Получить значение счетчика ингредиента')
    def get_ingredient_counter(self):
        try:
            counter_element = self.find_element(MainPageLocators.ingredient_counter)
            if counter_element.is_displayed():
                text = counter_element.text.strip()
                return int(text) if text else 0
            return 0
        except Exception:
            return 0

    # ===== Создание заказа через UI =====

    @allure.step('Нажать кнопку оформления заказа')
    def click_order_button(self):
        self.click_button(MainPageLocators.order_button)

    @allure.step('Получить номер заказа из модального окна (промежуточный)')
    def get_order_number_from_modal(self):
        try:
            order_number_element = self.wait_element_visible(
                MainPageLocators.order_modal, timeout=10
            )
            return order_number_element.text
        except Exception:
            return None

    @allure.step('Закрыть модальное окно заказа')
    def close_order_modal(self):
        try:
            self.click_button(MainPageLocators.close_order_modal)
        except Exception:
            self.force_close_modals()

    @allure.step('Получить финальный номер заказа из модального окна')
    def get_final_order_number(self, timeout=15):
        try:
            # Ждём, пока исчезнет «временный» номер (например, 9999)
            self.wait_for_element_to_disappear(
                MainPageLocators.order_number_loading, timeout=timeout
            )
            # затем ждём окончательный номер
            order_number_element = self.wait_element_visible(
                MainPageLocators.order_number_final, timeout=5
            )
            return order_number_element.text
        except Exception:
            return None

    @allure.step('Создать заказ через UI и получить финальный номер')
    def create_order_ui(self):
        """Создать заказ через UI и вернуть финальный номер"""
        # Перетаскиваем ингредиент в конструктор
        self.drag_ingredient_to_constructor()

        # Нажимаем кнопку оформления заказа
        self.click_order_button()

        # Ждём финальный номер
        order_number = self.get_final_order_number()

        # Закрываем модальное окно заказа
        self.close_order_modal()

        return order_number
