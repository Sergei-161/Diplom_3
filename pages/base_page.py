from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
import allure


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    # =============== URL / страница ===============

    @allure.step("Получить текущий URL")
    def get_current_url(self):
        return self.driver.current_url

    @allure.step("Ожидать, что URL содержит подстроку")
    def wait_url_contains(self, url_part, timeout=10):
        WebDriverWait(self.driver, timeout).until(EC.url_contains(url_part))

    @allure.step("Ожидать, что URL равен значению")
    def wait_url_to_be(self, url, timeout=10):
        WebDriverWait(self.driver, timeout).until(EC.url_to_be(url))

    @allure.step("Ждать загрузки страницы")
    def wait_for_page_load(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    @allure.step("Обновить страницу")
    def refresh_page(self):
        self.driver.refresh()

    # =============== Ожидания и поиск элементов ===============

    @allure.step("Ждать видимости элемента")
    def wait_element_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    @allure.step("Ждать кликабельности элемента")
    def wait_element_clickable(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    @allure.step("Найти элемент с ожиданием")
    def find_element_with_wait(self, locator, timeout=10):
        return self.wait_element_visible(locator, timeout)

    @allure.step("Найти элемент без ожидания")
    def find_element(self, locator):
        return self.driver.find_element(*locator)

    @allure.step("Найти несколько элементов без ожидания")
    def find_elements(self, locator):
        return self.driver.find_elements(*locator)

    # =============== Действия с элементами ===============

    @allure.step("Кликнуть по элементу")
    def click_button(self, locator, timeout=10):
        try:
            element = self.wait_element_clickable(locator, timeout)
            element.click()
        except Exception:
            # Fallback на JS-клик, если обычный не сработал
            element = self.wait_element_visible(locator, timeout)
            self.driver.execute_script("arguments[0].click();", element)

    @allure.step("Ввести текст в поле")
    def enter_text(self, locator, text, timeout=10):
        element = self.wait_element_visible(locator, timeout)
        element.clear()
        element.send_keys(text)

    @allure.step("Получить текст элемента")
    def get_element_text(self, locator, timeout=10):
        element = self.wait_element_visible(locator, timeout)
        return element.text

    @allure.step("Получить значение атрибута элемента")
    def get_element_attribute(self, locator, attribute, timeout=10):
        element = self.wait_element_visible(locator, timeout)
        return element.get_attribute(attribute)

    # =============== Проверки видимости ===============

    @allure.step("Проверить, что элемент видим")
    def is_element_visible(self, locator, timeout=5):
        try:
            self.wait_element_visible(locator, timeout)
            return True
        except Exception:
            return False

    @allure.step("Проверить, что элемент отображается")
    def is_element_displayed(self, locator, timeout=5):
        return self.is_element_visible(locator, timeout)

    @allure.step("Проверить, что элемент не виден")
    def is_element_not_visible(self, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    @allure.step("Проверить, что элемент не отображается")
    def is_element_not_displayed(self, locator, timeout=5):
        return self.is_element_not_visible(locator, timeout)

    @allure.step("Ждать, пока элемент исчезнет")
    def wait_for_element_to_disappear(self, locator, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )

    @allure.step("Ждать, пока элемент станет видимым и кликабельным")
    def wait_for_element_to_be_ready(self, locator, timeout=10):
        self.wait_element_visible(locator, timeout)
        self.wait_element_clickable(locator, timeout)

    # =============== Скролл / JS ===============

    @allure.step("Прокрутить к элементу")
    def scroll_to_element(self, locator, timeout=10):
        element = self.wait_element_visible(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    @allure.step("Прокрутить страницу вниз")
    def scroll_down(self, pixels=500):
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")

    @allure.step("Прокрутить страницу вверх")
    def scroll_up(self, pixels=500):
        self.driver.execute_script(f"window.scrollBy(0, -{pixels});")

    @allure.step("Выполнить JavaScript код")
    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)

    # =============== Мышь / drag-and-drop ===============

    @allure.step("Навести курсор на элемент")
    def hover_over_element(self, locator, timeout=10):
        element = self.wait_element_visible(locator, timeout)
        ActionChains(self.driver).move_to_element(element).perform()

    @allure.step("Дважды кликнуть по элементу")
    def double_click_element(self, locator, timeout=10):
        element = self.wait_element_visible(locator, timeout)
        ActionChains(self.driver).double_click(element).perform()

    @allure.step("Перетащить элемент в область")
    def drag_and_drop(self, source_locator, target_locator, timeout=10):
        """
        HTML5 drag&drop через DragEvent + DataTransfer.
        Работает в Firefox и Chrome. При проблемах есть fallback.
        """
        source = self.wait_element_visible(source_locator, timeout)
        target = self.wait_element_visible(target_locator, timeout)

        # на всякий случай — скроллим оба в видимую область
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", source)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)

        script = """
        const source = arguments[0];
        const target = arguments[1];

        function html5DragAndDrop(src, dst) {
            const dataTransfer = new DataTransfer();

            function fire(type, elem) {
                const event = new DragEvent(type, {
                    bubbles: true,
                    cancelable: true,
                    dataTransfer
                });
                elem.dispatchEvent(event);
            }

            fire('dragstart', src);
            fire('dragenter', dst);
            fire('dragover', dst);
            fire('drop', dst);
            fire('dragend', src);
        }

        function legacyDragAndDrop(src, dst) {
            function createEvent(type) {
                const event = document.createEvent('CustomEvent');
                event.initCustomEvent(type, true, true, null);
                event.dataTransfer = {
                    data: {},
                    setData: function(key, value) { this.data[key] = value; },
                    getData: function(key) { return this.data[key]; }
                };
                return event;
            }

            function dispatchEvent(element, event, transferData) {
                if (transferData !== undefined) {
                    event.dataTransfer = transferData;
                }
                if (element.dispatchEvent) {
                    element.dispatchEvent(event);
                } else if (element.fireEvent) {
                    element.fireEvent('on' + event.type, event);
                }
            }

            const dragStartEvent = createEvent('dragstart');
            dispatchEvent(src, dragStartEvent);

            const dragEnterEvent = createEvent('dragenter');
            dispatchEvent(dst, dragEnterEvent);

            const dragOverEvent = createEvent('dragover');
            dispatchEvent(dst, dragOverEvent);

            const dropEvent = createEvent('drop');
            dispatchEvent(dst, dropEvent, dragStartEvent.dataTransfer);

            const dragEndEvent = createEvent('dragend');
            dispatchEvent(src, dragEndEvent, dragStartEvent.dataTransfer);
        }

        try {
            html5DragAndDrop(source, target);
        } catch (e) {
            legacyDragAndDrop(source, target);
        }
        """
        self.driver.execute_script(script, source, target)

    @allure.step("Перетащить элемент по смещению")
    def drag_and_drop_by_offset(self, source_locator, x_offset, y_offset, timeout=10):
        source = self.wait_element_visible(source_locator, timeout)
        actions = ActionChains(self.driver)
        actions.click_and_hold(source).move_by_offset(x_offset, y_offset).release().perform()

    # =============== Табы / фреймы ===============

    @allure.step("Переключиться на вкладку по индексу")
    def switch_to_tab(self, index: int):
        self.driver.switch_to.window(self.driver.window_handles[index])

    @allure.step("Закрыть текущую вкладку")
    def close_current_tab(self):
        self.driver.close()

    @allure.step("Переключиться на iframe")
    def switch_to_iframe(self, locator, timeout=10):
        iframe = self.wait_element_visible(locator, timeout)
        self.driver.switch_to.frame(iframe)

    @allure.step("Вернуться из iframe")
    def switch_to_default_content(self):
        self.driver.switch_to.default_content()

    # =============== Модалки (главная страница) ===============

    @allure.step("Принудительно закрыть все модальные окна на главной странице")
    def force_close_modals(self, timeout=1, max_attempts=3):
        try:
            from locators.locators import MainPageLocators
        except Exception:
            return

        for _ in range(max_attempts):
            closed_any = False

            # крестик модалки ингредиента
            try:
                if self.is_element_visible(MainPageLocators.close_ingredient_modal, timeout=timeout):
                    self.click_button(MainPageLocators.close_ingredient_modal, timeout=timeout)
                    closed_any = True
            except Exception:
                pass

            # клик по оверлею
            try:
                if self.is_element_visible(MainPageLocators.modal_overlay, timeout=timeout):
                    self.click_button(MainPageLocators.modal_overlay, timeout=timeout)
                    closed_any = True
            except Exception:
                pass

            if not closed_any:
                break

    @allure.step("Закрыть все открытые модальные окна")
    def close_all_modals(self, timeout=1, max_attempts=3):
        self.force_close_modals(timeout=timeout, max_attempts=max_attempts)
